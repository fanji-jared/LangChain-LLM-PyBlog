import os


# 数据库配置
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'my-site')
MYSQL_USER = os.getenv('MYSQL_USER', 'fanji')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'fanji666')

# redis配置
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_DB = 0
REDIS_PASSWORD = None  # 如果你的Redis服务器没有密码，则留空
