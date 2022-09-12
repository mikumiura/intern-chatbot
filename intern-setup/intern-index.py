# Python 3.10.4
# Flask 2.1.2
# Flaskの公式ドキュメント：https://flask.palletsprojects.com/en/2.0.x/
# python3の公式ドキュメント：https://docs.python.org/ja/3.9/
# python3の基礎文法のわかりやすいサイト：https://note.nkmk.me/python/
# 使用するモジュールのインポート
# pythonが提供しているモジュールのインポート
import json
import logging
import urllib.request
from flask import Flask, request, Responce
# 自分で作成したモジュールのインポート
from database import Database

# Flaskクラスをnewしてappに代入
# gunicornの起動コマンドに使用しているのでここは変更しないこと
app = Flask(__name__)

# ログの設定
format = "%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"
logging.basicConfig(filename='/var/log/intern1/flask.log', level=logging.DEBUG, format=format, datefmt='%Y-%m-%d %H:%M:%S')

# 「/」にPOSTリクエストが来た場合、index関数が実行される
@app.route('/', methods=['post'])
def index():
    # 以下のコードでログを出力できる。出力先は「ログの設定」にあるファイル。コマンドラインに出力する場合はprintを使う。
    logging.debug("こんにちは!")
    # POSTリクエストのbodyを取得
    body_binary = request.get_data()
    body = json.loads(body_binary.decode())