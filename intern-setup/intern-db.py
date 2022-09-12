# 2022インターンではpymysqlを使用

import pymysql  # 参考: https://pymysql.readthedocs.io/en/latest/index.html
import logging

class Database(object):
    def __init__(self):
        # ログの設定
        format = "%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"
        logging.basicConfig(filename='/var/log/intern2/flask.log', level=logging.DEBUG, format=format, datefmt='%Y-%m-%d %H:%M:%S')