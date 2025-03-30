
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from datetime import datetime

def setup_loggers():
    # 创建日志级别列表
    log_levels = ['INFO', 'ERROR', 'DEBUG','WARNING','CRITICAL']
    #    获取当前日期
    current_date = datetime.now().strftime("%Y-%m-%d")
    # 为每个日志级别创建一个Logger对象
    for level in log_levels:
        logger = logging.getLogger(level)
        logger.setLevel(level)

        # 创建日志文件夹，如果不存在的话
        log_dir = f'/root/fast_web/logs/{level}'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        if os.path.exists(f'{log_dir}/{current_date}.log'):
            os.remove(f'{log_dir}/{current_date}.log')
        # 创建一个TimedRotatingFileHandler对象，每天凌晨创建新的日志文件
        handler = TimedRotatingFileHandler(f'{log_dir}/{current_date}.log', when='midnight', interval=1,backupCount=7)
        handler.suffix = '%Y-%m-%d.log'  # 设置新的日志文件的后缀，使用日期格式

        # 创建一个Formatter对象，设置日志消息的格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # 将TimedRotatingFileHandler对象添加到Logger对象
        logger.addHandler(handler)

# 使用Logger对象记录日志消息
# logging.getLogger('INFO').info('This is an info message.')
# logging.getLogger('ERROR').error('This is an error message.')
# logging.getLogger('DEBUG').debug('This is a debug message.')