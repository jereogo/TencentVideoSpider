# -*- coding: utf-8 -*-
"""
配置文件 - TencentVideoSpider
"""

# ========== 数据库配置 ==========
DB_HOST = 'localhost'              # MySQL 主机地址
DB_PORT = 3306                     # MySQL 端口
DB_USER = 'root'                   # MySQL 用户名
DB_PASSWORD = 'root'               # MySQL 密码 - 修改为你的密码
DB_NAME = 'tencent_video_db'       # 数据库名称
DB_CHARSET = 'utf8mb4'             # 数据库字符集

# ========== 爬虫配置 ==========
REQUEST_TIMEOUT = 10               # 请求超时时间（秒）
RETRY_TIMES = 3                    # 重试次数
RETRY_DELAY = 2                    # 重试延迟（秒）

# User-Agent 列表（用于伪装浏览器）
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
]

# 腾讯视频 URL
TENCENT_VIDEO_URL = 'https://v.qq.com'

# ========== 日志配置 ==========
LOG_LEVEL = 'INFO'                 # 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_FILE = 'logs/spider.log'       # 日志文件路径
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'  # 日志格式

# ========== 定时任务配置 ==========
SCHEDULE_INTERVAL = 3600           # 定时爬取间隔（秒）- 1小时更新一次
SCHEDULE_ENABLED = False           # 是否启用定时任务

# ========== 数据导出配置 ==========
EXPORT_FORMAT = 'csv'              # 导出格式: csv, excel, json
EXPORT_PATH = 'data/'              # 导出文件路径

# ========== 代理配置（可选） ==========
USE_PROXY = False                  # 是否使用代理
PROXY = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890',
}

# ========== 其他配置 ==========
MOVIE_LIMIT = 50                   # 爬取的电影数量限制
DEBUG_MODE = False                 # 调试模式