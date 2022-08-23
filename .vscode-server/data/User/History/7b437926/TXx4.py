from dotenv import load_dotenv
import os, pymysql.cursors
from logging import getLogger, FileHandler, DEBUG, Formatter

# ログの設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler(filename='/var/log/miura/flask.log')
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"))
logger.addHandler(handler)

# .envの読み込み
load_dotenv()

class DataBase:
    def __enter__(self):
        self.conn = pymysql.connect(
            host = os.environ["HOST"],
            port = int(os.environ["PORT"]),
            user = "root",
            password = os.environ["PWD"],
            db = os.environ["DB"],
            charset = "utf8mb4",
            cursorclass = pymysql.cursors.DictCursor
        )
        return self # ここでクラスを返さないとindex.pyでメソッド使用不可（デフォでdbに入るのはオブジェクトではなくここで返す値！！）

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    # uid未登録の場合usersテーブルにuidをインサート
    def insert_uid(self, user_id):
        try:
            with self.conn.cursor() as cursor:
                sql = "insert into `users` (uid) select %s where not exists (select * from `users` where uid = %s)"
                cursor.execute(sql, (user_id, user_id))
            self.conn.commit()
        except:
            logger.exception("exception happened.")

    # wordsテーブルからidを取得
    def select_words_id(self, input_text):
        words_id = None
        try:
            with self.conn.cursor() as cursor:
                sql = "select id from `words` where word = %s"
                cursor.execute(sql, input_text)
                words = cursor.fetchone()
        except:
            logger.exception("exception happened.")
        if words != None:
            words_id = words["id"]
        return words_id

    # usersテーブルからidを取得
    def select_users_id(self, user_id):
        users_id = None
        try:
            with self.conn.cursor() as cursor:
                sql = "select id from `users` where uid = %s"
                cursor.execute(sql, user_id)
                users = cursor.fetchone()
        except:
            logger.exception("exception happened.")
        if users != None:
            users_id = users["id"]
        return users_id

    # 該当wordがwordsテーブルにない場合インサート
    def insert_word(self, input_text):
        words_id = None
        try:
            with self.conn.cursor() as cursor:
                sql = "insert into `words` (word) values (%s)"
                cursor.execute(sql, input_text)
                words_id = cursor.lastrowid
            self.conn.commit()
        except:
            logger.exception("exception happened.")
        return words_id

    # urlsテーブルにurlをインサート
    def insert_url(self, wordsid_url_searchby_list):
        try:
            with self.conn.cursor() as cursor:
                sql = "insert into `urls` (words_id, url, search_by) values (%s, %s, %s)"
                cursor.executemany(sql, wordsid_url_searchby_list) # bulk insert
            self.conn.commit()
        except:
            logger.exception("exception happened.")

    # 中間テーブルにusers_idとwords_idをインサート
    # レコードの重複を除外
    def insert_to_userswords(self, users_id, words_id):
        try:
            with self.conn.cursor() as cursor:
                # sql = "insert into `users_words` (users_id, words_id) values (%s, %s)"
                sql = "insert into `users_words` (users_id, words_id) select %s, %s where not exists (select * from `users_words` where users_id = %s and `users_words`.words_id = %s)"
                cursor.execute(sql, (users_id, words_id, users_id, words_id))
            self.conn.commit()
        except:
            logger.exception("exception happened.")

    # urlを取得
    def select_url(self, users_id, words_id, search_by):
        url = None
        try:
            with self.conn.cursor() as cursor:
                sql = "select url, `users_words`.users_id from `words` left join `users_words` on `words`.id = `users_words`.words_id and `users_words`.users_id = %s inner join `urls` on `words`.id = `urls`.words_id where `words`.id = %s and `urls`.search_by = %s"
                cursor.execute(sql, (users_id, words_id, search_by))
                url = cursor.fetchall()
        except:
            logger.exception("exception happened.")
        return url

    # 前回の入力ワードをためておくだけ
    def insert_inputtext(self, user_id, input_text):
        try:
            with self.conn.cursor() as cursor:
                sql = "insert into `input_texts` (uid, word) values (%s, %s)"
                cursor.execute(sql, (user_id, input_text))
            self.conn.commit()
        except:
            logger.exception("exception happened.")

    # 前回の入力ワードを取得するだけ
    def select_inputtext(self, user_id):
        word = None
        try:
            with self.conn.cursor() as cursor:
                sql = "select word from `input_texts` where uid = %s order by id desc limit 1"
                cursor.execute(sql, user_id)
                word = cursor.fetchone()
        except:
            logger.exception("exception happened.")
        return word["word"]

    # # DBにあるAND検索のキーワードを取得
    # def select_word_andsearch(self, word):
    #     word_andsearch = None
    #     try:
    #         with self.conn.cursor() as cursor:
    #             sql = "select word from `words` where word like %s"
    #             cursor.execute(sql, (word + ' %'))
    #             word = cursor.fetchone()
    #     except:
    #         logger.exception("exception happened.")
    #     if word != None:
    #         word_andsearch = word["word"]
    #     return word_andsearch

    # DBにあるAND検索のキーワードを取得（fetchall版）
    def select_word_andsearch(self, word):
        word_andsearch = None
        try:
            with self.conn.cursor() as cursor:
                sql = "select word from `words` where word like %s"
                cursor.execute(sql, (word + ' %'))
                word_andsearch = cursor.fetchall()
                logger.debug(word_andsearch)
        except:
            logger.exception("exception happened.")
        return word_andsearch
    