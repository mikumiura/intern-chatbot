# Google検索ボット

# Python 3.9.6
# Flask 2.0.1
# Flaskの公式ドキュメント：https://flask.palletsprojects.com/en/2.0.x/
# python3の公式ドキュメント：https://docs.python.org/ja/3.9/
# python3の基礎文法のわかりやすいサイト：https://note.nkmk.me/python/

# 使用するモジュールのインポート
from glob import glob
from urllib import response
from flask import Flask, Response, request, render_template
from logging import getLogger, FileHandler, DEBUG, Formatter
from line import post_to_line
from google import Google, google_search
from twitter import twitter_search
from database import DataBase
from dotenv import load_dotenv
import json

# Flaskクラスをnewしてappに代入 # Flaskのインスタンス
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
    user_id = body["events"][0]["source"]["userId"]
    
    # 検索したいワードが入力されたとき -> googleとtwitterどちらで検索するか選択できるポストバックメッセージを送信
    if body["events"][0]["type"] == "message" and body["events"][0]["message"]["type"] == "text":
        input_text = body["events"][0]["message"]["text"]

        if body["events"][0]["message"]["text"] == "検索をやめる":
            post_to_line(reply_token, [{"type": "sticker", "packageId": "789", "stickerId": "10862"}])

        with DataBase() as db:
            db.insert_inputtext(user_id, input_text)

        post_to_line(
            reply_token,
            [{
                "type":"text",
                "text":"どっちで検索しますか？",
                "quickReply": {
                    "items": [
                        {
                            "type": "action",
                            "action": {
                                "type": "postback",
                                "label": "google",
                                "data": "google",
                                "displayText": "google"
                            }
                        },
                        {
                            "type": "action",
                            "action": {
                                "type": "postback",
                                "label": "twitter",
                                "data": "twitter",
                                "displayText": "twitter"
                            }
                        }
                    ]
                }
            }]
            )

    # ポストバックで「google」が指定されたとき
    elif body["events"][0]["postback"]["data"] == "google":
        google_search(user_id, reply_token)
        
    # ポストバックで「twitter」が指定されたとき
    elif body["events"][0]["postback"]["data"] == "twitter":
        twitter_search(user_id, reply_token)

    # 以下のコードで200OKを返す
    status_code = Response(status=200)
    return status_code


# "https://miura.tobila-techintern.com/"にgetリクエストが来たら実行する関数
# htmlを読み込むために用意されてるrender_template()を使う
@app.route('/', methods=['get'])
def read_first_page():
    return render_template("first-page.html")

    # file = "templates/first-page.html"
    # with open(file) as f:
    #     resp = f.read()
    # return resp

@app.route('/test1', methods=['post'])
def submit_data():
    body_binary = request.get_data()
    body_decode = body_binary.decode()
    body = json.loads(body_decode)

    star_rate = body["rate"]
    review_comment = body["comment"]

    global avg_star_rate
    global zero_stars_comment
    global one_star_comment
    global two_stars_comment
    global three_stars_comment
    global four_stars_comment
    global five_stars_comment

    with DataBase() as db:
        db.insert_review(star_rate, review_comment)
        avg_star_rate = db.select_avg_starrate()
        zero_stars_comment = db.select_review_comment(0)
        one_star_comment = db.select_review_comment(1)
        two_stars_comment = db.select_review_comment(2)
        three_stars_comment = db.select_review_comment(3)
        four_stars_comment = db.select_review_comment(4)
        five_stars_comment = db.select_review_comment(5)

    # 以下のコードで200OKを返す
    status_code = Response(status=200)
    return status_code

@app.route('/test2', methods=['get'])
def read_next_page():
    file = "templates/next-page.html"
    with open(file) as f:
        resp = f.read()
    return resp

    # return render_template(
    #     "next-page.html",
    #     average_rate=avg_star_rate,
    #     zero_stars=zero_stars_comment,
    #     one_star=one_star_comment,
    #     two_stars=two_stars_comment,
    #     three_stars=three_stars_comment,
    #     four_stars=four_stars_comment,
    #     five_stars=five_stars_comment
    #     )