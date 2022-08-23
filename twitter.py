from logging import getLogger, FileHandler, DEBUG, Formatter
from database import DataBase
from line import post_to_line
import os, tweepy

# ログの設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler(filename='/var/log/miura/flask.log')
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"))
logger.addHandler(handler)

# ツイート取得
def get_tweets(input_text):
    consumer_key = os.environ["CONSUMER_KEY"]
    consumer_secret = os.environ["CONSUMER_SECRET"]
    access_token = os.environ["ACCESS_TOKEN"]
    access_token_secret = os.environ["ACCESS_TOKEN_SECRET"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    search_word = input_text + " filter:images min_faves:5000"

    tweets = tweepy.Cursor(api.search_tweets, q=search_word).items(5)

    tw_data = []
    for tweet in tweets:
        tw_data.append(tweet.entities)
    url_list = []
    for u in tw_data:
        if not u["urls"]:
            url_list.append(u["media"][-1]["expanded_url"])
        else:
            url_list.append(u["urls"][-1]["expanded_url"])
    
    return url_list

def twitter_search(user_id, reply_token):
    # ポストバック直前の入力ワードをinput_textsから取得
    word = None
    with DataBase() as db:
        word = db.select_inputtext(user_id)

    # 該当のuidが存在しない場合はここでusersテーブルにインサート
    # wordsテーブルとusersテーブルからそれぞれid取得
    with DataBase() as db:
        db.insert_uid(user_id)
        words_id = db.select_words_id(word)
        users_id = db.select_users_id(user_id)

    # 入力ワードでまだ誰も検索していないとき
    if words_id == None:
        # wordsテーブルにwordをインサート
        with DataBase() as db:
            words_id = db.insert_word(word) # このwords_idはlastrowidで取得したものなので辞書型にはならない

        # twitter検索処理
        url_list = get_tweets(word)

        if not url_list:
            post_to_line(reply_token, [{"type": "text", "text": "検索結果がありません。"}])

        else:
            url = "\n\n".join(url_list)
            post_to_line(reply_token, [{"type": "text", "text": url}])

            wordsid_url_searchby_list = []
            for u in url_list:
                wordsid_url_searchby_list.append([words_id, u, "twitter"])

            # urlとsearch_byのインサート、中間テーブルへのidの追加
            with DataBase() as db:
                db.insert_url(wordsid_url_searchby_list)
                db.insert_to_userswords(users_id, words_id)

    # 入力ワードの検索履歴がDBにあったとき
    else:
        # search_byを条件に入れてurlを取得
        with DataBase() as db:
            google_u_list = db.select_url(users_id, words_id, "google")
            twitter_u_list = db.select_url(users_id, words_id, "twitter")

        # twitterで検索したurlが存在しないとき
        if not twitter_u_list:
            # googleで検索はしたがurlを取得できなかったとき
            if not google_u_list:
                post_to_line(reply_token, [{"type": "text", "text": "検索結果がありません。"}])
            # googleでの検索履歴はあったとき -> twitter検索
            else:
                twitter_url_list = get_tweets(word)

                if not twitter_url_list:
                    post_to_line(reply_token, [{"type": "text", "text": "ごめんさがしたけどなかった"}])
                
                else:
                    url = "\n\n".join(twitter_url_list)
                    post_to_line(reply_token, [{"type": "text", "text": url}])

                    wordsid_url_searchby_list = []
                    for u in twitter_url_list:
                        wordsid_url_searchby_list.append([words_id, u, "twitter"])

                    # urlと検索手段のインサート、中間テーブルへのidの追加
                    with DataBase() as db:
                        db.insert_url(wordsid_url_searchby_list)
                        db.insert_to_userswords(users_id, words_id)

        else:
            url_list = []
            userswords_usersid = None
            for u in twitter_u_list:
                url_list.append(u["url"])
                userswords_usersid = u["users_id"]

            url = "\n\n".join(url_list)
            post_to_line(reply_token, [{"type": "text", "text": url}])
            
            # users_wordsのusers_idがNone（他人の検索履歴しかないが自分も検索した）のとき、自分のusers_idをインサート
            if userswords_usersid == None:
                with DataBase() as db:
                    db.insert_to_userswords(users_id, words_id)
