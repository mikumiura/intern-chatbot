from dotenv import load_dotenv
import os, pymysql.cursors

# .envの読み込み
load_dotenv()

# mariaの参照
def maria_select(user_id) -> str:
    connection_select = pymysql.connect(
        host=os.environ["HOST"],
        port=int(os.environ["PORT"]),
        user="root",
        password=os.environ["PWD"],
        db=os.environ["DB"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with connection_select.cursor() as cursor:
            # create new table
            sql_select = "select word from tweets where uid = " + user_id + " order by id desc limit 1"
            cursor.execute(sql_select)
            for word in cursor:
                return word
        # connection is not autocommit by dafault. So you must commit to save your changes.
        connection_select.commit()
    finally:
        connection_select.close()
