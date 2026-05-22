# 腾讯视频电影热度排行榜爬虫

> 一个简洁高效的爬虫项目，用于爬取腾讯视频平台的电影热度排行榜数据并进行数据存储与分析展示

## 📋 项目简介

本项目旨在爬取腾讯视频平台的电影热度排行榜，将实时数据存储到 MySQL 数据库中，并提供数据查询和可视化功能。适合作为大专毕业设计项目。

## ✨ 主要功能

- ✅ 定时爬取腾讯视频电影排行榜数据
- ✅ 自动存储到 MySQL 数据库
- ✅ 记录排行榜历史变化
- ✅ 提供数据查询和导出功能
- ✅ 简洁清晰的日志输出

## 🛠️ 技术栈

| 技术 | 说明 |
|------|------|
| Python 3.8+ | 编程语言 |
| requests | HTTP 请求库 |
| BeautifulSoup4 | HTML 解析库 |
| MySQL | 数据库 |
| APScheduler | 定时任务调度 |
| pandas | 数据处理 |

## 📦 项目结构

```
TencentVideoSpider/
├── main.py                  # 程序主入口
├── spider.py                # 爬虫核心代码
├── db.py                    # 数据库操作模块
├── config.py                # 配置文件
├── requirements.txt         # 依赖包列表
├── sql/
│   └── init_db.sql          # 数据库初始化脚本
├── logs/                    # 日志文件目录
├── data/                    # 数据导出目录
└── README.md                # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

**系统要求**：Windows 10+ / macOS / Linux  
**Python 版本**：3.8 或更高

### 2. 安装依赖

```bash
# 克隆项目
git clone https://github.com/jereogo/TencentVideoSpider.git
cd TencentVideoSpider

# 安装依赖包
pip install -r requirements.txt
```

### 3. 数据库配置

#### 步骤1：创建 MySQL 数据库

```sql
CREATE DATABASE tencent_video_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### 步骤2：运行初始化脚本

```bash
# 使用 MySQL 客户端导入 SQL 文件
mysql -u your_username -p tencent_video_db < sql/init_db.sql
```

或在 MySQL 客户端中执行：

```sql
USE tencent_video_db;
SOURCE sql/init_db.sql;
```

### 4. 配置文件修改

编辑 `config.py`，修改你的 MySQL 连接信息：

```python
# config.py
DB_HOST = 'localhost'      # MySQL 主机
DB_PORT = 3306             # MySQL 端口
DB_USER = 'root'           # MySQL 用户名
DB_PASSWORD = 'your_password'  # MySQL 密码
DB_NAME = 'tencent_video_db'   # 数据库名
```

### 5. 运行爬虫

```bash
# 单次爬取
python main.py

# 或者启动定时爬虫（每小时更新一次）
python main.py --schedule
```

## 📊 数据库设计

### 表结构说明

#### `movies` 表 - 电影信息表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INT | 主键 |
| movie_name | VARCHAR(255) | 电影名称 |
| rank | INT | 排行名次 |
| hotness | INT | 热度值 |
| url | VARCHAR(500) | 电影链接 |
| created_at | DATETIME | 爬取时间 |

## 📈 使用示例

### 查看最新排行榜

```python
from spider import TencentVideoSpider

# 创建爬虫实例
spider = TencentVideoSpider()

# 爬取数据
spider.crawl()

# 查看结果
spider.display_results()
```

### 查询数据库

```python
from db import DatabaseManager

# 创建数据库连接
db = DatabaseManager()

# 查询前10名电影
movies = db.query_top_movies(limit=10)
for movie in movies:
    print(f"{movie['rank']}. {movie['movie_name']} - 热度: {movie['hotness']}")
```

## 🔧 配置说明

### config.py 详细配置

```python
# 数据库配置
DB_HOST = 'localhost'           # MySQL 服务器地址
DB_PORT = 3306                  # MySQL 端口
DB_USER = 'root'                # 数据库用户名
DB_PASSWORD = 'password'        # 数据库密码
DB_NAME = 'tencent_video_db'    # 数据库名

# 爬虫配置
REQUEST_TIMEOUT = 10            # 请求超时时间（秒）
RETRY_TIMES = 3                 # 重试次数
RETRY_DELAY = 5                 # 重试延迟（秒）

# 日志配置
LOG_LEVEL = 'INFO'              # 日志级别
LOG_FILE = 'logs/spider.log'    # 日志文件路径

# 定时任务配置
SCHEDULE_INTERVAL = 3600        # 定时爬取间隔（秒）
```

## 📝 日志输出

程序会在 `logs/` 目录下生成日志文件，记录每次爬取的详细信息：

```
2026-05-22 14:30:15 - INFO - 开始爬取腾讯视频电影排行榜
2026-05-22 14:30:18 - INFO - 成功获取 50 条电影数据
2026-05-22 14:30:20 - INFO - 数据已保存到数据库
```

## 🐛 常见问题

### Q1: 连接数据库失败？

**A**: 检查以下几点：
- MySQL 服务是否启动
- 用户名和密码是否正确
- config.py 中的数据库配置是否正确

### Q2: 爬虫获取不到数据？

**A**: 可能原因：
- 网络连接问题，检查网络
- 腾讯视频网页结构改变，需要更新选择器
- User-Agent 被识别为爬虫，可以更换 UA

### Q3: 如何修改爬取间隔？

**A**: 编辑 `config.py` 中的 `SCHEDULE_INTERVAL` 参数。

## 📚 学习资源

- [Requests 文档](https://requests.readthedocs.io/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [MySQL 文档](https://dev.mysql.com/doc/)
- [Python 官方文档](https://docs.python.org/3/)

## 📄 许可证

MIT License

## 👨‍💻 作者

jereogo - 大专毕业设计项目

## 🤝 反馈与建议

如有任何问题或建议，欢迎提出 Issue 或 Pull Request。

---

**祝你毕设顺利！** 🎓✨