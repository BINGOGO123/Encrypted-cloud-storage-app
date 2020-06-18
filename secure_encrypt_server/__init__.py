import logging
from config.logger import logger_server
import os
import datetime
from django.conf import settings

# 初始化日志对象
def initialLogger():
  # 如果不存在logs文件夹则创建
  if not os.path.exists(os.path.join(settings.BASE_DIR,"logs/")):
    os.mkdir(os.path.join(settings.BASE_DIR,"logs/"))
  handler1 = logging.FileHandler(os.path.join(settings.BASE_DIR,"logs/secure_encrypt_serever." + str(datetime.date.today()) + ".log"),"a",encoding="utf8")
  handler2 = logging.StreamHandler()
  formatter1 = logging.Formatter(fmt="%(asctime)s [%(levelname)s] [%(lineno)d] >> %(message)s",datefmt="%Y-%m-%d %H:%M:%S")
  formatter2 = logging.Formatter(fmt = "[%(levelname)s] >> %(message)s")
  handler1.setFormatter(formatter1)
  handler2.setFormatter(formatter2)
  handler1.setLevel(logging.DEBUG)
  handler2.setLevel(logging.INFO)
  logger_server.setLevel(logging.DEBUG)
  logger_server.addHandler(handler1)
  logger_server.addHandler(handler2)

initialLogger()