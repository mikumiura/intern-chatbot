# Google検索ボット

# Python 3.9.6
# Flask 2.0.1
# Flaskの公式ドキュメント：https://flask.palletsprojects.com/en/2.0.x/
# python3の公式ドキュメント：https://docs.python.org/ja/3.9/
# python3の基礎文法のわかりやすいサイト：https://note.nkmk.me/python/

# 使用するモジュールのインポート
from flask import Flask, Response, request
from logging import getLogger, FileHandler, DEBUG, Formatter
from line import post_to_line
from google import Google
from database import DataBase
from dotenv import load_dotenv
import json

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

    reply_token = body["events"][0]["replyToken"]

    # ユーザが文字列を入力した場合
    if ("message" in body["events"][0]["type"]) and (body["events"][0]["message"]["type"] == "text"):

        input_text = body["events"][0]["message"]["text"]
        user_id = body["events"][0]["source"]["userId"]

        # with DataBase() as db:
        #     db.insert(user_id, input_text)
        #     num = db.select(user_id, input_text)

        g = Google()
        g.search(input_text)
        g.get_url()

    # 以下のコードで200OKを返す
    status_code = Response(status=200)
    return status_code