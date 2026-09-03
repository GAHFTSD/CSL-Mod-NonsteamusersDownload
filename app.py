from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np

app = Flask(__name__)

# 加载 JSON，保持日期为字符串
df = pd.read_json('data_clean.json', encoding='utf-8', convert_dates=False)

# 确保必要列存在
if 'published' not in df.columns:
    df['published'] = None
if 'updated' not in df.columns:
    df['updated'] = None

df['published'] = df['published'].astype(object).where(pd.notnull(df['published']), None)
df['updated'] = df['updated'].astype(object).where(pd.notnull(df['updated']), None)

# 为计算添加临时年份列
df['year'] = pd.to_datetime(df['published'], errors='coerce').dt.year

# ---------- 页面路由 ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- API 1：分页/搜索/筛选 ----------
@app.route('/api/mods')
def get_mods():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))

    filtered = df
    if category:
        filtered = filtered[filtered['category'] == category]
    if search:
        filtered = filtered[filtered['name'].str.contains(search, case=False)]

    total = len(filtered)
    data = filtered.iloc[offset:offset+limit].to_dict(orient='records')
    return jsonify({'total': total, 'data': data})

# ---------- API 2：基础统计（只保留总数、类别数、最新上传） ----------
@app.route('/api/stats')
def get_stats():
    valid_dates = df['published'].dropna()
    latest = valid_dates.max() if not valid_dates.empty else '-'
    
    stats = {
        'total': int(len(df)),
        'categories': df['category'].value_counts().to_dict(),
        'latest': latest
    }
    return jsonify(stats)

# ---------- API 3：年度趋势 ----------
@app.route('/api/trend')
def get_trend():
    temp_year = pd.to_datetime(df['published'], errors='coerce').dt.year
    trend_df = df.assign(year=temp_year).groupby(['year', 'category']).size().reset_index(name='count')
    years = sorted(trend_df['year'].dropna().unique().astype(int).tolist())
    categories = df['category'].unique()
    
    datasets = []
    for cat in categories:
        cat_data = trend_df[trend_df['category'] == cat]
        counts = []
        for y in years:
            val = cat_data[cat_data['year'] == y]['count']
            if not val.empty:
                counts.append(int(val.iloc[0]))
            else:
                counts.append(0)
        datasets.append({
            'label': cat,
            'data': counts,
            'borderWidth': 2,
            'fill': False
        })
    
    return jsonify({'labels': years, 'datasets': datasets})

# ---------- API 4：文件大小直方图 ----------
@app.route('/api/size_dist')
def get_size_dist():
    sizes = df['size_mb'].dropna()
    if sizes.empty:
        return jsonify({'bins': [], 'counts': []})
    
    hist, bin_edges = pd.cut(sizes, bins=10, retbins=True)
    bin_labels = [f"{round(bin_edges[i], 1)}-{round(bin_edges[i+1], 1)}" for i in range(len(bin_edges)-1)]
    counts = [int(x) for x in hist.value_counts().sort_index().tolist()]
    
    return jsonify({'labels': bin_labels, 'counts': counts})

# ---------- API 5：更新活跃度 ----------
@app.route('/api/update_activity')
def get_update_activity():
    pub = pd.to_datetime(df['published'], errors='coerce')
    upd = pd.to_datetime(df['updated'], errors='coerce')
    interval = (upd - pub).dt.days
    activity = df.assign(interval=interval).groupby('category')['interval'].mean().reset_index().dropna()
    activity = activity.sort_values('interval')
    
    return jsonify({
        'categories': activity['category'].tolist(),
        'avg_days': [round(float(x), 1) for x in activity['interval'].tolist()]
    })

# ---------- API 6：未来预测（线性回归） ----------
@app.route('/api/forecast')
def get_forecast():
    temp_year = pd.to_datetime(df['published'], errors='coerce').dt.year
    trend_df = df.assign(year=temp_year).groupby(['year', 'category']).size().reset_index(name='count')
    categories = df['category'].unique()
    years = sorted(trend_df['year'].dropna().unique().astype(int).tolist())
    
    if len(years) < 2:
        return jsonify({})
    
    next_year = max(years) + 1
    result = {}
    
    for cat in categories:
        cat_df = trend_df[trend_df['category'] == cat]
        if len(cat_df) < 3:
            continue
        
        x = cat_df['year'].values.astype(float)
        y = cat_df['count'].values.astype(float)
        coeffs = np.polyfit(x, y, 1)
        slope, intercept = coeffs[0], coeffs[1]
        
        pred_val = max(0, int(round(slope * next_year + intercept)))
        history = {int(year): int(count) for year, count in zip(cat_df['year'], cat_df['count'])}
        
        result[cat] = {
            'history': history,
            'forecast': {int(next_year): pred_val},
            'slope': round(float(slope), 2)
        }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)