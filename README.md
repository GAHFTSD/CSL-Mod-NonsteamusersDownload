# Cities: Skylines 模组数据采集与统计可视化平台

> 本项目仅供学习、研究和技术交流使用，**禁止用于任何商业用途**。

---

## 项目出发点

《城市：天际线》拥有庞大的模组生态，但 **EPIC 平台用户** 和 **非 Steam 玩家** 难以直接访问创意工坊，第三方模组站缺乏系统的检索与数据洞察。  
本平台旨在：

- 为非 Steam 用户提供便捷的模组浏览和下载辅助；
- 通过 **数据统计 + 趋势预测** 揭示模组生态发展规律；
- 展示 **从爬虫、清洗、分析到可视化部署** 的完整技术链路。

---

## 项目落地全流程

| 阶段 | 技术实现 |
|------|----------|
| **数据采集** | Scrapy 爬取 `smods.ru`，字段含名称、类别、大小、日期、链接等，存入 MySQL，其中，ANPMYSQL.py是完全自定义的内容，依据实际情况使用。 |
| **数据清洗** | Pandas 统一大小单位（KB→MB）、格式化日期、计算“更新间隔”衍生特征。 |
| **后端 API** | Flask 提供 6 个 REST 接口：分页查询、统计、趋势、直方图、活跃度、线性回归预测。 |
| **前端可视化** | Bootstrap 5 + Chart.js，含粘性统计卡片、趋势/预测组合图、直方图、活跃度柱状图、可搜索/筛选/分页的表格，悬停显示模组图片。 |
| **配置管理** | 首次运行交互式输入数据库信息，自动生成 `db_config.json`，后续一键执行，敏感文件不入库。 |
| **版本控制与部署** | 托管于 GitHub，可部署至 PythonAnywhere 等云平台。 |

---

## 🛠️ 技术栈

- **爬虫**：Scrapy, PyMySQL  
- **数据处理**：Pandas, NumPy  
- **后端**：Flask  
- **前端**：Bootstrap 5, Chart.js  
- **数据库**：MySQL  
- **工具**：Git, JSON 配置管理

---

## 🚀 快速开始

### 环境要求
- Python 3.10+
- MySQL 5.7+（已创建数据库，例如 `cslmods`）

### 1. 克隆项目
```bash
git clone https://github.com/GAHFTSD/CSL-Mod-NonsteamusersDownload.git
cd CSL-Mod-NonsteamusersDownload
```
### 2.安装依赖
```bash
pip install -r requirements.txt
```
### 3.配置数据库并导出数据
```bash
python export_data.py
```
### 4.启动 Web 服务
```bash
python app.py
```
### 5.重新爬取 （若项目以及停止更新需在 SKYLINES/spiders/ 目录下执行）
```bash
scrapy crawl skyline -o output.json
```

## 📁 项目结构
```text
CSL-Mod-NonsteamusersDownload/
├── SKYLINES/              # Scrapy 爬虫模块（含 ANPMYSQL.py、pipelines.py 等）
├── templates/
│   └── index.html         # 前端页面
├── app.py                 # Flask 后端 API
├── export_data.py         # 数据清洗与配置引导脚本
├── data_clean.json        # 清洗后的数据（自动生成）
├── requirements.txt       # 依赖清单
├── .gitignore             # 忽略 db_config.json 等敏感文件
└── README.md              # 本文档
```

## ⚠️ 免责声明 & 致歉
- 非商业用途：禁止将本项目或数据用于任何商业目的。
- 尊重网站政策：爬虫应遵守目标网站的 robots.txt 及服务条款，设置合理间隔。
- 用户责任：使用者自行承担所有法律及道德风险，开发者不承担任何责任。
- 数据用途限制：仅用于统计分析和学术研究，不涉及隐私或版权内容。
- 侵权删除：如侵犯权益，请联系我们，核实后将立即删除相关数据。
- 致歉：爬虫对 smods.ru 造成了额外负担和模组制作者造成了潜在的负担，深表歉意。如源站不愿被采集，我将即刻停止。

## 📧 联系方式
- 作者：Airlin Neleftari Prismriver (GAHFTSD)
- 邮箱：gahftsd@hotmail.com
- B站：https://space.bilibili.com/104341778
- GitHub：https://github.com/GAHFTSD/CSL-Mod-NonsteamusersDownload
## 📄 License
详见 LICENSE 文件

最后更新：2026年9月
