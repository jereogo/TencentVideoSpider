# -*- coding: utf-8 -*-
"""
爬虫核心模块 - TencentVideoSpider
负责爬取腾讯视频电影排行榜数据
"""

import requests
from bs4 import BeautifulSoup
import logging
import random
import time
from config import (
    REQUEST_TIMEOUT, RETRY_TIMES, RETRY_DELAY, USER_AGENTS,
    TENCENT_VIDEO_URL, LOG_LEVEL, USE_PROXY, PROXY, MOVIE_LIMIT
)
from db import DatabaseManager

# 配置日志
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TencentVideoSpider:
    """腾讯视频爬虫类"""
    
    def __init__(self):
        """初始化爬虫"""
        self.session = requests.Session()
        self.db = DatabaseManager()
        self.movies = []
        self.setup_session()
    
    def setup_session(self):
        """设置会话参数"""
        # 随机选择 User-Agent
        self.session.headers.update({
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': TENCENT_VIDEO_URL,
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })
        
        # 配置代理
        if USE_PROXY:
            self.session.proxies.update(PROXY)
            logger.info("✓ 已配置代理")
    
    def get_headers(self):
        """获取请求头"""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Referer': TENCENT_VIDEO_URL,
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        return headers
    
    def fetch_page(self, url, retry=0):
        """
        获取网页内容
        
        参数:
            url: 要爬取的 URL
            retry: 重试次数
        
        返回:
            str: 网页内容，失败返回 None
        """
        try:
            logger.info(f"正在请求: {url}")
            response = self.session.get(
                url,
                headers=self.get_headers(),
                timeout=REQUEST_TIMEOUT,
                verify=False
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            logger.info(f"✓ 请求成功 (状态码: {response.status_code})")
            return response.text
        except requests.exceptions.Timeout:
            logger.warning(f"✗ 请求超时，准备重试 ({retry}/{RETRY_TIMES})")
            if retry < RETRY_TIMES:
                time.sleep(RETRY_DELAY)
                return self.fetch_page(url, retry + 1)
            return None
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"✗ 连接错误，准备重试 ({retry}/{RETRY_TIMES}): {e}")
            if retry < RETRY_TIMES:
                time.sleep(RETRY_DELAY)
                return self.fetch_page(url, retry + 1)
            return None
        except Exception as e:
            logger.error(f"✗ 请求失败: {e}")
            return None
    
    def parse_movie_list(self, html):
        """
        解析电影列表
        
        参数:
            html: 网页 HTML 内容
        
        返回:
            list: 电影列表
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            self.movies = []
            
            # 寻找电影排行榜容器
            # 注：选择器可能需要根据实际网页结构调整
            movie_items = soup.find_all('div', class_='item')
            
            if not movie_items:
                logger.warning("✗ 未找到电影列表，可能需要更新选择器")
                # 尝试备选选择器
                movie_items = soup.find_all('li', class_='item')
            
            if not movie_items:
                logger.warning("✗ 仍未找到电影列表")
                return []
            
            logger.info(f"找到 {len(movie_items)} 个电影项")
            
            rank = 1
            for item in movie_items[:MOVIE_LIMIT]:
                try:
                    # 提取电影信息
                    movie_name_elem = item.find('h3') or item.find('a')
                    if not movie_name_elem:
                        continue
                    
                    movie_name = movie_name_elem.get_text(strip=True)
                    
                    # 获取链接
                    link_elem = item.find('a')
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = TENCENT_VIDEO_URL + url
                    
                    # 获取热度值
                    hotness_elem = item.find('span', class_='hot')
                    if not hotness_elem:
                        hotness_elem = item.find('span', class_='num')
                    
                    hotness = 0
                    if hotness_elem:
                        hotness_text = hotness_elem.get_text(strip=True)
                        # 提取数字
                        import re
                        numbers = re.findall(r'\d+', hotness_text)
                        if numbers:
                            hotness = int(numbers[0])
                    
                    # 获取评分
                    rating_elem = item.find('span', class_='score')
                    rating = 0
                    if rating_elem:
                        rating_text = rating_elem.get_text(strip=True)
                        try:
                            rating = float(rating_text)
                        except:
                            pass
                    
                    movie = {
                        'rank': rank,
                        'movie_name': movie_name,
                        'hotness': hotness,
                        'url': url,
                        'rating': rating,
                        'category': '电影',
                        'description': ''
                    }
                    
                    self.movies.append(movie)
                    logger.debug(f"解析电影: {rank}. {movie_name} (热度: {hotness})")
                    rank += 1
                
                except Exception as e:
                    logger.warning(f"解析电影项时出错: {e}")
                    continue
            
            logger.info(f"✓ 成功解析 {len(self.movies)} 部电影")
            return self.movies
        
        except Exception as e:
            logger.error(f"✗ 解析电影列表失败: {e}")
            return []
    
    def crawl(self, url=None):
        """
        执行爬取操作
        
        参数:
            url: 爬取的 URL，如果为空则使用默认 URL
        
        返回:
            bool: 是否爬取成功
        """
        try:
            if not url:
                # 使用腾讯视频电影排行榜 URL
                # 注：这是一个示例 URL，实际可能需要调整
                url = 'https://v.qq.com/channel/movie?sort=1&offset=0'
            
            logger.info("=" * 50)
            logger.info("开始爬取腾讯视频电影排行榜")
            logger.info("=" * 50)
            
            # 获取网页
            html = self.fetch_page(url)
            if not html:
                logger.error("✗ 获取网页失败")
                return False
            
            # 解析电影列表
            self.parse_movie_list(html)
            
            if not self.movies:
                logger.warning("✗ 未获取到电影数据")
                return False
            
            # 保存到数据库
            count = self.db.batch_insert_movies(self.movies)
            
            if count > 0:
                logger.info("=" * 50)
                logger.info(f"✓ 爬取成功！共保存 {count} 条电影数据")
                logger.info("=" * 50)
                return True
            else:
                logger.error("✗ 数据保存失败")
                return False
        
        except Exception as e:
            logger.error(f"✗ 爬取过程中出错: {e}")
            return False
    
    def display_results(self):
        """显示爬取结果"""
        if not self.movies:
            print("\n暂无数据")
            return
        
        print("\n" + "=" * 60)
        print("腾讯视频电影热度排行榜")
        print("=" * 60)
        
        for movie in self.movies[:20]:  # 显示前20部
            print(f"{movie['rank']:2d}. {movie['movie_name']:30s} | 热度: {movie['hotness']:6d} | 评分: {movie['rating']}")
        
        print("=" * 60)
    
    def get_movies(self):
        """获取爬取的电影列表"""
        return self.movies
    
    def close(self):
        """关闭爬虫，释放资源"""
        if self.db:
            self.db.close()


if __name__ == '__main__':
    # 测试爬虫
    spider = TencentVideoSpider()
    
    # 执行爬取
    success = spider.crawl()
    
    if success:
        # 显示结果
        spider.display_results()
        
        # 从数据库查询���显示
        movies = spider.db.get_latest_movies(limit=10)
        print("\n数据库中最新的10部电影：")
        for movie in movies:
            print(f"{movie['rank']}. {movie['movie_name']} - 热度: {movie['hotness']}")
    
    spider.close()