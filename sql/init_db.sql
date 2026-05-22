-- 数据库初始化脚本
-- TencentVideoSpider

-- 创建电影表
CREATE TABLE IF NOT EXISTS movies (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    movie_name VARCHAR(255) NOT NULL COMMENT '电影名称',
    rank INT NOT NULL DEFAULT 0 COMMENT '排行名次',
    hotness INT NOT NULL DEFAULT 0 COMMENT '热度值',
    url VARCHAR(500) COMMENT '电影链接',
    category VARCHAR(50) DEFAULT '电影' COMMENT '电影分类',
    rating DECIMAL(3, 1) DEFAULT 0 COMMENT '评分',
    description TEXT COMMENT '电影描述',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_rank (rank) COMMENT '排行名次索引',
    INDEX idx_created_at (created_at) COMMENT '创建时间索引',
    INDEX idx_hotness (hotness) COMMENT '热度索引',
    FULLTEXT INDEX ft_movie_name (movie_name) COMMENT '电影名称全文索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='电影信息表';

-- 创建爬虫日志表（可选）
CREATE TABLE IF NOT EXISTS crawl_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    crawl_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '爬取时间',
    status VARCHAR(20) COMMENT '爬取状态（success/fail）',
    movie_count INT DEFAULT 0 COMMENT '爬取电影数量',
    error_message TEXT COMMENT '错误信息',
    execution_time INT COMMENT '执行耗时（秒）'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='爬虫执行日志表';

-- 创建统计表（可选）
CREATE TABLE IF NOT EXISTS statistics (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键ID',
    stat_date DATE UNIQUE COMMENT '统计日期',
    total_movies INT DEFAULT 0 COMMENT '总电影数',
    avg_hotness INT DEFAULT 0 COMMENT '平均热度',
    max_hotness INT DEFAULT 0 COMMENT '最高热度',
    min_hotness INT DEFAULT 0 COMMENT '最低热度',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='统计数据表';

-- 创建视图：最新排行榜
CREATE OR REPLACE VIEW v_latest_ranking AS
SELECT 
    m.rank,
    m.movie_name,
    m.hotness,
    m.rating,
    m.url,
    m.category,
    m.created_at
FROM movies m
WHERE m.created_at = (SELECT MAX(created_at) FROM movies)
ORDER BY m.rank ASC;

-- 创建视图：热度排行
CREATE OR REPLACE VIEW v_hotness_ranking AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY hotness DESC) AS ranking,
    movie_name,
    hotness,
    rating,
    created_at
FROM movies
WHERE created_at = (SELECT MAX(created_at) FROM movies)
ORDER BY hotness DESC;

-- 插入示例数据（测试用）
-- INSERT INTO movies (movie_name, rank, hotness, url, category, rating, description) VALUES
-- ('示例电影1', 1, 100000, 'https://v.qq.com/x/cover/xxx', '电影', 8.5, '这是一部示例电影'),
-- ('示例电影2', 2, 95000, 'https://v.qq.com/x/cover/xxx', '电影', 8.2, '这是另一部示例电影');

-- 授权用户
-- GRANT ALL PRIVILEGES ON tencent_video_db.* TO 'spider_user'@'localhost' IDENTIFIED BY 'spider_password';
-- FLUSH PRIVILEGES;

-- 创建完成提示
-- SELECT '✓ 数据库初始化完成' AS status;