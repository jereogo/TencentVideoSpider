# -*- coding: utf-8 -*-
"""
数据库管理模块 - TencentVideoSpider
负责所有数据库操作
"""

import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DB_CHARSET

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        """初始化数据库连接"""
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                charset=DB_CHARSET,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
            logger.info("✓ 数据库连接成功")
        except Error as e:
            logger.error(f"✗ 数据库连接失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            logger.info("✓ 数据库连接已关闭")
    
    def insert_movie(self, movie_name, rank, hotness, url, category='电影', rating=0, description=''):
        """
        插入电影数据到数据库
        
        参数:
            movie_name: 电影名称
            rank: 排行名次
            hotness: 热度值
            url: 电影链接
            category: 分类
            rating: 评分
            description: 描述
        
        返回:
            bool: 是否插入成功
        """
        try:
            query = """
                INSERT INTO movies (movie_name, rank, hotness, url, category, rating, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (movie_name, rank, hotness, url, category, rating, description, datetime.now())
            self.cursor.execute(query, values)
            self.connection.commit()
            return True
        except Error as e:
            logger.error(f"✗ 插入数据失败: {e}")
            return False
    
    def batch_insert_movies(self, movies):
        """
        批量插入电影数据
        
        参数:
            movies: 电影列表，每个元素是包含电影信息的字典
        
        返回:
            int: 插入的记录数
        """
        try:
            query = """
                INSERT INTO movies (movie_name, rank, hotness, url, category, rating, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values_list = []
            for movie in movies:
                values = (
                    movie.get('movie_name', ''),
                    movie.get('rank', 0),
                    movie.get('hotness', 0),
                    movie.get('url', ''),
                    movie.get('category', '电影'),
                    movie.get('rating', 0),
                    movie.get('description', ''),
                    datetime.now()
                )
                values_list.append(values)
            
            self.cursor.executemany(query, values_list)
            self.connection.commit()
            logger.info(f"✓ 成功插入 {len(values_list)} 条电影数据")
            return len(values_list)
        except Error as e:
            logger.error(f"✗ 批量插入数据失败: {e}")
            return 0
    
    def query_top_movies(self, limit=10, order_by='rank'):
        """
        查询热度最高的电影
        
        参数:
            limit: 查询数量限制
            order_by: 排序字段
        
        返回:
            list: 电影列表
        """
        try:
            query = f"""
                SELECT * FROM movies 
                ORDER BY {order_by} ASC 
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            return results
        except Error as e:
            logger.error(f"✗ 查询数据失败: {e}")
            return []
    
    def query_by_name(self, movie_name):
        """
        按电影名称查询
        
        参数:
            movie_name: 电影名称
        
        返回:
            list: 电影列表
        """
        try:
            query = "SELECT * FROM movies WHERE movie_name LIKE %s ORDER BY created_at DESC"
            self.cursor.execute(query, (f"%{movie_name}%",))
            results = self.cursor.fetchall()
            return results
        except Error as e:
            logger.error(f"✗ 查询数据失败: {e}")
            return []
    
    def get_latest_movies(self, limit=50):
        """
        获取最新爬取的电影数据
        
        参数:
            limit: 数量限制
        
        返回:
            list: 电影列表
        """
        try:
            query = """
                SELECT * FROM movies 
                WHERE created_at = (SELECT MAX(created_at) FROM movies)
                ORDER BY rank ASC
                LIMIT %s
            """
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            return results
        except Error as e:
            logger.error(f"✗ 查询数据失败: {e}")
            return []
    
    def get_statistics(self):
        """
        获取统计信息
        
        返回:
            dict: 统计信息
        """
        try:
            # 总电影数
            self.cursor.execute("SELECT COUNT(*) as total FROM movies")
            total = self.cursor.fetchone()['total']
            
            # 最后更新时间
            self.cursor.execute("SELECT MAX(created_at) as last_update FROM movies")
            last_update = self.cursor.fetchone()['last_update']
            
            # 平均热度
            self.cursor.execute("SELECT AVG(hotness) as avg_hotness FROM movies")
            avg_hotness = self.cursor.fetchone()['avg_hotness']
            
            return {
                'total': total,
                'last_update': last_update,
                'avg_hotness': round(avg_hotness, 2) if avg_hotness else 0
            }
        except Error as e:
            logger.error(f"✗ 获取统计信息失败: {e}")
            return {}
    
    def clear_old_data(self, days=7):
        """
        清理超过指定天数的旧数据
        
        参数:
            days: 天数
        
        返回:
            int: 删除的记录数
        """
        try:
            query = """
                DELETE FROM movies 
                WHERE created_at < DATE_SUB(NOW(), INTERVAL %s DAY)
            """
            self.cursor.execute(query, (days,))
            self.connection.commit()
            deleted = self.cursor.rowcount
            logger.info(f"✓ 清理 {deleted} 条旧数据")
            return deleted
        except Error as e:
            logger.error(f"✗ 清理数据失败: {e}")
            return 0
    
    def export_to_csv(self, filename):
        """
        导出数据到 CSV 文件
        
        参数:
            filename: 文件名
        
        返回:
            bool: 是否导出成功
        """
        try:
            import pandas as pd
            query = "SELECT * FROM movies ORDER BY created_at DESC, rank ASC"
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            df = pd.DataFrame(results)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            logger.info(f"✓ 数据已导出到 {filename}")
            return True
        except Exception as e:
            logger.error(f"✗ 导出数据失败: {e}")
            return False


if __name__ == '__main__':
    # 测试数据库连接
    try:
        db = DatabaseManager()
        
        # 获取统计信息
        stats = db.get_statistics()
        print(f"\n=== 数据库统计信息 ===")
        print(f"总电影数: {stats.get('total', 0)}")
        print(f"最后更新: {stats.get('last_update', '暂无数据')}")
        print(f"平均热度: {stats.get('avg_hotness', 0)}")
        
        # 查询最新数据
        movies = db.get_latest_movies(limit=10)
        if movies:
            print(f"\n=== 最新电影排行榜（前10名） ===")
            for movie in movies:
                print(f"{movie['rank']}. {movie['movie_name']} - 热度: {movie['hotness']}")
        else:
            print("\n暂无数据，请先运行爬虫收集数据")
        
        db.close()
    except Exception as e:
        print(f"错误: {e}")