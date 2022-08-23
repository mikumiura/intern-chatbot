## こっち本物！！！

# Python 3.9.6
# Flask 2.0.1
# Flaskの公式ドキュメント：https://flask.palletsprojects.com/en/2.0.x/
# python3の公式ドキュメント：https://docs.python.org/ja/3.9/
# python3の基礎文法のわかりやすいサイト：https://note.nkmk.me/python/


# 使用するモジュールのインポート
from pickle import FALSE
from flask import Flask, Response, request
from logging import getLogger, FileHandler, DEBUG, Formatter
from dotenv import load_dotenv
import json, requests, os, tweepy, pymysql.cursors

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

# .envファイルの読み込み
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

    # 文字以外の入力があった時
    if body["events"][0]["message"]["type"] != "text":
        # LINEPlatformへのPOSTリクエスト
        post_url = "https://api.line.me/v2/bot/message/reply"
        replyToken = body["events"][0]["replyToken"]
        header = {
            "Authorization": os.environ["BEARER_TOKEN"]
            }
        payload = {
            "replyToken": replyToken,
            "messages": [
                {
                    "type": "text",
                    "text": "YOUR INPUT WAS INVALID"
                }
            ]
        }
        requests.post(url=post_url, json=payload, headers=header)

    # # LINEへのリプライトークン
    # replyToken = body["events"][0]["replyToken"]
    # 辞書型に変換したbodyから本文（text）を取り出してinput_textに格納
    input_text = body["events"][0]["message"]["text"]

    # クイックリプライで「別のワードで検索」が返ってきた時
    if input_text == "別のワードで検索":
        # LINEPlatformへのPOSTリクエスト
        post_url = "https://api.line.me/v2/bot/message/reply"
        replyToken = body["events"][0]["replyToken"]
        header = {
            "Authorization": os.environ["BEARER_TOKEN"]
            }
        payload = {
            "replyToken": replyToken,
            "messages": [
                {
                    "type": "text",
                    "text": "検索したいキーワードを入力してください"
                }
            ]
        }
        requests.post(url=post_url, json=payload, headers=header)

    # クイックリプライで「検索をやめる」が返ってきた時
    elif input_text == "検索をやめる":
        # LINEPlatformへのPOSTリクエスト
        post_url = "https://api.line.me/v2/bot/message/reply"
        replyToken = body["events"][0]["replyToken"]
        header = {
            "Authorization": os.environ["BEARER_TOKEN"]
            }
        payload = {
            "replyToken": replyToken,
            "messages": [
                {
                    "type": "sticker",
                    "packageId": "789",
                    "stickerId": "10862"
                }
            ]
        }
        requests.post(url=post_url, json=payload, headers=header)


    # 「別のワードで検索」「検索をやめる」以外の文字列が返ってきた時
    else:
        # TwitterAPIへのGETリクエスト
        consumer_key = os.environ["CONSUMER_KEY"]
        consumer_secret = os.environ["CONSUMER_SECRET"]
        access_token = os.environ["ACCESS_TOKEN"]
        access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)

        search_word = input_text + " filter:images min_faves:1000"

        tweets = tweepy.Cursor(api.search_tweets, q=search_word).items(1)

        ## こっちのリスト使うならまあまあたくさんツイート取得する必要あり
        ## いいね5000件以上のツイートを何基準で取ってきたかわからんツイートたちの中から抽出するので
        # over_5000_fav = []
        # for tweet in tweets:
        #     if tweet.favorite_count >= 5000:
        #         over_5000_fav.append(tweet.entities)
        # logger.debug(over_5000_fav)

        tw_data = []
        for tweet in tweets:
            tw_data.append(tweet.entities)
        logger.debug(tw_data)

        t_data = []

        # ツイートを取得できなかった場合
        if tw_data == []:
            # LINEPlatformへのPOSTリクエスト
            post_url = "https://api.line.me/v2/bot/message/reply"
            replyToken = body["events"][0]["replyToken"]
            header = {
                "Authorization": os.environ["BEARER_TOKEN"]
                }
            payload = {
                "replyToken": replyToken,
                "messages": [
                    {
                        "type": "text",
                        "text": "ツイートを取得できませんでした"
                    },
                    {
                        "type": "sticker",
                        "packageId": "789",
                        "stickerId": "10877"
                    }
                ]
            }
            requests.post(url=post_url, json=payload, headers=header)

        # ツイートを取得できた場合
        else:
            ## expanded_urlの位置によっては今後改良する
            for i in tw_data:
                if i["urls"] == []:
                    t_data.append(i["media"][0]["expanded_url"])
                elif len(i["urls"]) == 2:
                    t_data.append(i["urls"][1]["expanded_url"])
                else:
                    t_data.append(i["urls"][0]["expanded_url"])

                hoge = i.keys()
                logger.debug(hoge)
                
            # Mariaにデータ追加
            connection_insert = pymysql.connect(
                host="127.0.0.1",
                port=3306,
                user="root",
                password="hogehoge-123",
                db="miura",
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

            # Mariaの参照
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
                        w = word
                # connection is not autocommit by dafault. So you must commit to save your changes.
                connection_select.commit()
            finally:
                connection_select.close()

            # LINEPlatformへのPOSTリクエスト
            post_url = "https://api.line.me/v2/bot/message/reply"
            replyToken = body["events"][0]["replyToken"]
            header = {
                "Authorization": os.environ["BEARER_TOKEN"]
                }
            payload = {
                "replyToken": replyToken,
                "messages": [
                    {
                        "type": "text",
                        "text": t_data[0]
                    },
                    {
                        "type": "text",
                        "text": "前回のキーワードで検索しますか？",
                        "quickReply": {
                            "items": [
                                {
                                    "type": "action",
                                    "action": {
                                        "type": "message",
                                        "label": "はい", 
                                        "text": w["word"]
                                    }
                                },
                                {
                                    "type": "action",
                                    "action": {
                                        "type": "message",
                                        "label": "別のワードで検索",
                                        "text": "別のワードで検索"
                                    }
                                },
                                {
                                    "type": "action",
                                    "action": {
                                        "type": "message",
                                        "label": "検索をやめる",
                                        "text": "検索をやめる"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
            
            requests.post(url=post_url, json=payload, headers=header)

    # 以下のコードで200OKを返す
    status_code = Response(status=200)
    return status_code