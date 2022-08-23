from dotenv import load_dotenv
import os, pymysql.cursors

# .envの読み込み
load_dotenv()

# mariaにデータ追加
def maria_insert(input_text, ci):
    connection_insert = ci
    try:
        with connection_insert.cursor() as cursor:
            # create new table
            sql_insert = "insert into `tweets` (word) values (%s) "
            cursor.execute(sql_insert, input_text)
        # connection is not autocommit by dafault. So you must commit to save your changes.
        connection_insert.commit()
    finally:
        connection_insert.close()
