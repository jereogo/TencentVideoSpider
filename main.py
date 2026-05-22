# -*- coding: utf-8 -*-
"""
主程序入口 - TencentVideoSpider
"""

import sys
import logging
import argparse
from datetime import datetime
from spider import TencentVideoSpider
from db import DatabaseManager
from apscheduler.schedulers.background import BackgroundScheduler
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/spider.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def print_banner():
    """打印欢迎信息"""
    banner = """
    ╔════════════════════════════════════════╗
    ║   腾讯视频电影热度排行榜爬虫           ║
    ║   TencentVideoSpider v1.0               ║
    ╚════════════════════════════════════════╝
    """
    print(banner)


def single_crawl():
    """执行单次爬取"""
    print_banner()
    logger.info("开始执行单次爬取任务")
    
    try:
        spider = TencentVideoSpider()
        
        # 执行爬取
        success = spider.crawl()
        
        if success:
            logger.info("✓ 爬取成功")
            spider.display_results()
            
            # 显示统计信息
            stats = spider.db.get_statistics()
            print("\n" + "=" * 60)
            print("数据库统计信息")
            print("=" * 60)
            print(f"数据库中的总电影数: {stats.get('total', 0)}")
            print(f"最后更新时间: {stats.get('last_update', '暂无')}")
            print(f"平均热度: {stats.get('avg_hotness', 0)}")
            print("=" * 60)
        else:
            logger.error("✗ 爬取失败")
            sys.exit(1)
        
        spider.close()
    
    except KeyboardInterrupt:
        logger.info("用户中断了程序")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序出错: {e}")
        sys.exit(1)


def scheduled_crawl():
    """执行定时爬取"""
    print_banner()
    logger.info("启动定时爬虫模式")
    
    spider = None
    
    def job():
        """定时任务"""
        nonlocal spider
        try:
            logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 执行定时爬取任务...")
            if spider is None:
                spider = TencentVideoSpider()
            
            success = spider.crawl()
            if success:
                logger.info("✓ 定时爬取成功")
            else:
                logger.warning("✗ 定时爬取失败")
        
        except Exception as e:
            logger.error(f"定时任务执行出错: {e}")
    
    try:
        # 创建定时任务调度器
        scheduler = BackgroundScheduler()
        
        # 每小时执行一次
        scheduler.add_job(job, 'interval', hours=1, id='crawl_job')
        
        # 启动调度器
        scheduler.start()
        logger.info("✓ 定时爬虫已启动，每小时执行一次")
        logger.info(f"首次爬取将在 1 小时后进行，或按 Ctrl+C 停止")
        
        # 立即执行一次
        logger.info("执行初始爬取...")
        job()
        
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("用户中断了程序")
            scheduler.shutdown()
            if spider:
                spider.close()
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"定时爬虫启动失败: {e}")
        if spider:
            spider.close()
        sys.exit(1)


def query_database():
    """查询数据库中的数据"""
    print_banner()
    
    try:
        db = DatabaseManager()
        
        print("\n" + "=" * 60)
        print("数据库中的电影数据")
        print("=" * 60)
        
        # 获取最新的电影数据
        movies = db.get_latest_movies(limit=20)
        
        if movies:
            print(f"\n最新爬取时间的电影排行榜（共 {len(movies)} 部）:")
            print("-" * 60)
            for movie in movies:
                print(f"{movie['rank']:2d}. {movie['movie_name']:30s} | 热度: {movie['hotness']:6d}")
        else:
            print("数据库中暂无数据，请先执行爬取任务")
        
        # 显示统计信息
        stats = db.get_statistics()
        print("\n" + "-" * 60)
        print(f"数据库中的总电影数: {stats.get('total', 0)}")
        print(f"最后更新时间: {stats.get('last_update', '暂无')}")
        print(f"平均热度: {stats.get('avg_hotness', 0)}")
        print("=" * 60)
        
        db.close()
    
    except Exception as e:
        logger.error(f"查询失败: {e}")
        sys.exit(1)


def export_data(filename='data/movies_export.csv'):
    """导出数据到 CSV 文件"""
    print_banner()
    
    try:
        db = DatabaseManager()
        success = db.export_to_csv(filename)
        
        if success:
            logger.info(f"✓ 数据已成功导出到: {filename}")
        else:
            logger.error("✗ 数据导出失败")
        
        db.close()
    
    except Exception as e:
        logger.error(f"导出失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='腾讯视频电影热度排行榜爬虫',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py              # 执行单次爬取
  python main.py --schedule   # 启动定时爬虫
  python main.py --query      # 查询数据库
  python main.py --export     # 导出数据
        """
    )
    
    parser.add_argument('--schedule', action='store_true', help='启动定时爬虫模式（每小时执行一次）')
    parser.add_argument('--query', action='store_true', help='查询数据库中的电影数据')
    parser.add_argument('--export', action='store_true', help='导出数据到 CSV 文件')
    parser.add_argument('--file', type=str, default='data/movies_export.csv', help='导出文件名（默认: data/movies_export.csv）')
    
    args = parser.parse_args()
    
    if args.schedule:
        # 启动定时爬虫
        scheduled_crawl()
    elif args.query:
        # 查询数据库
        query_database()
    elif args.export:
        # 导出数据
        export_data(args.file)
    else:
        # 默认执行单次爬取
        single_crawl()


if __name__ == '__main__':
    main()