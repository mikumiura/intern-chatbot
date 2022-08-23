import os, requests

# LINEへのpostリクエスト
def post_to_line(rt, msg):
    # LINEPlatformへのPOSTリクエスト
    post_url = "https://api.line.me/v2/bot/message/reply"
    replyToken = rt
    header = {
        "Authorization": os.environ["BEARER_TOKEN"]
        }
    payload = {
        "replyToken": replyToken,
        "messages": msg
    }
    requests.post(url=post_url, json=payload, headers=header)
