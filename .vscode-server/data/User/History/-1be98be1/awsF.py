from dotenv import load_dotenv
import os, pymysql.cursors

# .envの読み込み
load_dotenv()

# mariaにデータ追加
def maria_insert(input_text):
    connection_insert = pymysql.connect(
        host=os.environ["HOST"],
        port=int(os.environ["PORT"]),
        user="root",
        password=os.environ["PWD"],
        db=os.environ["DB"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
        )
    try:
        with connection_insert.cursor() as cursor:
            # create new table
            sql_insert = "insert into `tweets` (word) values (%s) "
            cursor.execute(sql_insert, input_text)
        # connection is not autocommit by dafault. So you must commit to save your changes.
        connection_insert.commit()
    finally:
        connection_insert.close()
