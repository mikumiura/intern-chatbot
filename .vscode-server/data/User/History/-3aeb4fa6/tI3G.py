import os, tweepy

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
    for u in url_list:
        if not u["urls"]:
            url_list.append(u["media"][-1]["expanded_url"])
        else:
            url_list.append(u["urls"][-1]["expanded_url"])
    
    return url_list
