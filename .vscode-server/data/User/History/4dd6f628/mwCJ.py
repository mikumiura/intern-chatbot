from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from logging import getLogger, FileHandler, DEBUG, Formatter
from database import DataBase
from line import post_to_line
from bs4 import BeautifulSoup
import chromedriver_binary, requests

# ログの設定
logger = getLogger(__name__)
logger.setLevel(DEBUG)
handler = FileHandler(filename='/var/log/miura/flask.log')
handler.setLevel(DEBUG)
handler.setFormatter(Formatter("%(asctime)s: %(levelname)s: %(pathname)s: line %(lineno)s: %(message)s"))
logger.addHandler(handler)

options = Options()
options.add_argument("--headless")

# google検索処理
class Google:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()

    def search(self, input_text):
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.google.com/")
        # assert "Google" in driver.title # タイトルにGoogleという単語が含まれているかを確認するアサーション
        self.elem = self.driver.find_element(By.NAME, "q")
        self.elem.clear()
        self.elem.send_keys(input_text) # ユーザから受け取ったワードで検索
        self.elem.send_keys(Keys.RETURN)
    
    # サイトのurlを取得
    def get_url(self):
        count = 0
        url = []
        for e in self.driver.find_elements(By.XPATH, "//a/h3"): # 記事のタイトル名がとれてる
            self.elem_a = e.find_element(By.XPATH, "..") # 一個上のディレクトリ（aタグ）に移動
            self.elem_url = self.elem_a.get_attribute("href") # aタグに格納されているurlを取得
            count += 1
            if count > 5:
                break
            url.append(self.elem_url)
        return url
        # assert "No results found." not in driver.page_source

    # 他のキーワードを取得
    def get_other_keyword(self):
        other_keywords = []
        for o in self.driver.find_elements(By.XPATH, "//a/div[2]/b"):
            other_keywords.append(o.text)
        return other_keywords

def google_search(user_id, reply_token):
    # ポストバック直前に入力された文字列をinput_textsから取得
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

        # google検索処理
        with Google() as g:
            g.search(word)
            url_list = g.get_url()

        if not url_list:
            post_to_line(reply_token, [{"type": "text", "text": "検索結果がありません。"}])

        else:
            url = "\n\n".join(url_list)
            post_to_line(reply_token, [{"type": "text", "text": url}])

            wordsid_url_searchby_list = []
            for u in url_list:
                wordsid_url_searchby_list.append([words_id, u, "google"])

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

        # googleで検索したurlが存在しないとき
        if not google_u_list:
            # twitterで検索はしたがurlを取得できなかったとき
            if not twitter_u_list:
                post_to_line(reply_token, [{"type": "text", "text": "検索結果がありません。"}])
            # twitterでの検索履歴はあったとき -> google検索
            else:
                with Google() as g:
                    g.search(word)
                    google_url_list = g.get_url()
                    google_other_keyword_list = g.get_other_keyword()
                    logger.debug(google_other_keyword_list)

                if not google_url_list:
                    post_to_line(reply_token, [{"type": "text", "text": "ごめんさがしたけどなかった"}])
                
                else:
                    url = "\n\n".join(google_url_list)
                    for o in google_other_keyword_list:
                        post_to_line(
                            reply_token,
                            [
                                {
                                    "type": "text",
                                    "text": url
                                },
                                {
                                    "type": "text",
                                    "text": "他の人は次のキーワードでも検索しています。",
                                    "quickReply": {
                                        "items": [
                                            {
                                                "type": "action",
                                                "action": {
                                                    "type": "message",
                                                    "label": o,
                                                    "text": o
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
                        )

                    wordsid_url_searchby_list = []
                    for u in google_url_list:
                        wordsid_url_searchby_list.append([words_id, u, "google"])

                    # urlと検索手段のインサート、中間テーブルへのidの追加
                    with DataBase() as db:
                        db.insert_url(wordsid_url_searchby_list)
                        db.insert_to_userswords(users_id, words_id)

        # googleでの検索履歴がDBにあったとき
        else:
            url_list = []
            userswords_usersid = None
            for u in google_u_list:
                url_list.append(u["url"])
                userswords_usersid = u["users_id"]

            url = "\n\n".join(url_list)

            ## DBに「入力したワード hoge」みたいな検索履歴があったとき -> レコメンド
            word_andsearch = None
            with DataBase() as db:
                word_andsearch = db.select_word_andsearch(word)
            
            if word_andsearch == None:
                post_to_line(reply_token, [{"type": "text", "text": url}])
            else:
                post_to_line(
                    reply_token,
                    [
                        {
                            "type": "text",
                            "text": url
                        },
                        {
                            "type": "text",
                            "text": "「" + word + "」で検索した人は「" + word_andsearch + "」でも検索しています。"
                        },
                        {
                            "type": "text",
                            "text": "「" + word_andsearch + "」でも検索しますか？",
                            "quickReply": {
                                "items": [
                                    {
                                        "type": "action",
                                        "action": {
                                            "type": "message",
                                            "label": "はい",
                                            "text": word_andsearch
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
                )
            
            # users_wordsのusers_idがNone（他人の検索履歴しかないが自分も検索した）のとき、自分のusers_idをインサート
            if userswords_usersid == None:
                with DataBase() as db:
                    db.insert_to_userswords(users_id, words_id)