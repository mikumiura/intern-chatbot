# Google検索ボット

# Python 3.9.6
# Flask 2.0.1
# Flaskの公式ドキュメント：https://flask.palletsprojects.com/en/2.0.x/
# python3の公式ドキュメント：https://docs.python.org/ja/3.9/
# python3の基礎文法のわかりやすいサイト：https://note.nkmk.me/python/

# 使用するモジュールのインポート
from this import d
from flask import Flask, Response, request
from logging import getLogger, FileHandler, DEBUG, Formatter
from line import post_to_line
from google import Google
from google_db import DataBase
from dotenv import load_dotenv
import json, pprint

# Flaskクラスをnewしてappに代入
# gunicornの起動コマンドに使用しているのでここは変更しないこと
app = Flask(__name__)

# ログの設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler(filename='/var/log/miura/flask.log')
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"))
logger.addHandler(handler)

# .envの読み込み
load_dotenv()

# 「/」にPOSTリクエストが来た場合、index関数が実行される
@app.route('/', methods=['post'])
def index():
    # 受信したPOSTリクエストのbodyを取得
    body_binary = request.get_data()
    # 取得したbodyはバイナリなので、デコードして文字列にする
    body_decode = body_binary.decode()
    # 文字列（JSON）を辞書型にする
    body = json.loads(body_decode)
    logger.debug(body)

    reply_token = body["events"][0]["replyToken"]
    input_text = body["events"][0]["message"]["text"]
    user_id = body["events"][0]["source"]["userId"]

    # DBからそのユーザが検索したワード一覧を取り出す
    with DataBase() as db:
        w_list = db.select_word(user_id)
        word_list = []
        for w in w_list:
            word_list.append(w["word"])

    # ユーザが初めてそのワードを入力した時
    if input_text not in word_list:
        # uidとwordをインサートし、一意に決まるidを取得
        with DataBase() as db:
            id = db.insert_word(user_id, input_text)

        # google検索処理
        g = Google()
        g.search(input_text)
        url_list = g.get_url()
        g.session_close()

        if not url_list:
            post_to_line(reply_token, [{"type":"text", "text":"検索結果がありません。"}])

        elif len(url_list) <= 5:
            # url整形してLINEに投げる
            url = "\n\n".join(url_list)
            post_to_line(reply_token, [{"type":"text", "text":url}])

            # urlをDBに貯める(BulkInsert)
            bulk = []
            for u in url_list:
                bulk.append([id, u])
            with DataBase() as db:
                db.insert_url(bulk)

    # ユーザが過去にそのワードを入力していて、DBに検索履歴が残っていた時
    else:
        # DBからidを取得し、idからurlを取得（リストで返ってくる）
        with DataBase() as db:
            id = db.select_id(user_id, input_text)
            u_list = db.select_url(id["id"])

        url_list = []
        for u in u_list:
            url_list.append(u["url"])
        
        if not url_list: # url_listが空
            post_to_line(reply_token, [{"type":"text", "text":"検索結果がありません。"}])
        
        else:
            # url整形してLINEに投げる
            url = "\n\n".join(url_list)
            post_to_line(reply_token, [{"type":"text", "text":url}])


    # 以下のコードで200OKを返す
    status_code = Response(status=200)
    return status_code


# ユーザが文字列を入力した場合(最初から文字列入力しか想定していない場合はこれいらん)
# if ("message" in body["events"][0]["type"]) and (body["events"][0]["message"]["type"] == "text"):
