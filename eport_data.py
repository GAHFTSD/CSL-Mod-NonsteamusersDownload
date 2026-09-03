import pymysql
import pandas as pd
import json
import os

# ---------- 配置文件管理（与 ANPMYSQL.py 共享同一个文件） ----------
CONFIG_FILE = 'db_config.json'

def get_db_config():
    """尝试读取本地配置文件，若不存在或缺失字段则引导用户输入"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if all(k in config.get('mysql', {}) for k in ['host', 'user', 'password', 'database']):
                    return config['mysql']
        except:
            pass  # 文件损坏则重新创建
    
    # ---- 交互输入（NeedToType 环节） ----
    print("📝 未检测到有效的数据库配置，请按提示输入（输入后将保存至 db_config.json，下次自动加载）：")
    host = input("请输入 MySQL 主机地址 (回车默认 127.0.0.1): ") or "127.0.0.1"
    user = input("请输入 MySQL 用户名 (回车默认 root): ") or "root"
    password = input("请输入 MySQL 密码 (直接回车则为空): ")
    database = input("请输入 数据库名称 (回车默认 cslmods): ") or "cslmods"  
    
    config_data = {
        "mysql": {
            "host": host,
            "user": user,
            "password": password,
            "database": database,
            "charset": "utf8mb4"
        }
    }
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4)
    print("✅ 配置已保存至 db_config.json，下次运行将自动跳过此步骤。\n")
    return config_data['mysql']

# ---------- 主程序 ----------
if __name__ == "__main__":
    # 1. 获取配置（首次弹输入，之后自动读取）
    db_conf = get_db_config()

    # 2. 连接数据库
    conn = pymysql.connect(
        host=db_conf['host'],
        user=db_conf['user'],
        password=db_conf['password'],
        database=db_conf['database'],
        charset=db_conf.get('charset', 'utf8mb4')
    )
    print(f"✅ 已连接到数据库: {db_conf['database']}")

    # 3. 读取数据
    df = pd.read_sql("SELECT * FROM CITYSKYLINESMODS", conn)
    conn.close()

    # 4. 清洗数据
    def parse_size(size_str):
        if not size_str: return None
        if 'MB' in size_str: return float(size_str.replace(' MB', '').replace('MB', '').strip())
        elif 'KB' in size_str: return float(size_str.replace(' KB', '').replace('KB', '').strip()) / 1024
        return None

    df['size_mb'] = df['filesize'].apply(parse_size)
    df['publishdate'] = pd.to_datetime(df['publishdate'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['upgradedate'] = pd.to_datetime(df['upgradedate'], errors='coerce').dt.strftime('%Y-%m-%d')

    df.rename(columns={
        'modname': 'name', 'modlink': 'link', 'modimg': 'image',
        'modattr': 'category', 'publishdate': 'published',
        'upgradedate': 'updated', 'downloadurl': 'download',
        'steamlink': 'steam', 'filesize': 'size_raw'
    }, inplace=True)

    df_clean = df[['id', 'name', 'category', 'size_mb', 'published', 'updated', 'steam', 'download', 'image']]

    # 5. 导出 JSON
    df_clean.to_json('data_clean.json', orient='records', force_ascii=False)
    print(f"✅ 导出成功！共 {len(df_clean)} 条记录。")
    print(f"📊 类别分布:\n{df_clean['category'].value_counts()}")