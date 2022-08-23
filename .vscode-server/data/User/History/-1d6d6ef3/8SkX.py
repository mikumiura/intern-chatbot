import os, requests

# LINEへのpostリクエスト
def post_to_line(token, msg):
    # LINEPlatformへのPOSTリクエスト
    post_url = "https://api.line.me/v2/bot/message/reply"
    replyToken = token
    header = {
        "Authorization": os.environ["BEARER_TOKEN"]
        }
    payload = {
        "replyToken": replyToken,
        "messages": msg
    }
    requests.post(url=post_url, json=payload, headers=header)
