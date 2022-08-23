import pymysql.cursors

# mariaの参照
def maria_select() -> str:
    connection_select = pymysql.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="hogehoge-123",
        db="miura",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor
    )
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
