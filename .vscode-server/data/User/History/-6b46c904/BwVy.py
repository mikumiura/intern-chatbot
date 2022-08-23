from dotenv import load_dotenv
import os, pymysql.cursors

# .envの読み込み
load_dotenv()

# mariaの参照
def maria_select(ci) -> str:
    connection_select = ci
    try:
        with connection_select.cursor() as cursor:
            # create new table
            sql_select = "select word from tweets order by id desc limit 1"
            cursor.execute(sql_select)
            for word in cursor:
                return word
        # connection is not autocommit by dafault. So you must commit to save your changes.
        connection_select.commit()
    finally:
        connection_select.close()
