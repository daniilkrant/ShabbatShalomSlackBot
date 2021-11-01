import datetime

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

token = ""
message_blocks = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "Shabbat Shalom! :flag-il:\n:flag-il: !שַׁבָּת שָׁלוֹם",
            "emoji": True
        }
    },
    {
        "type": "image",
        "title": {
            "type": "plain_text",
            "text": " ",
            "emoji": True
        },
        "image_url": "https://w2.chabad.org/media/images/1029/OlAJ10294609.jpg",
        "alt_text": "marg"
    }
]

sunset_api_url = "https://api.sunrise-sunset.org/json"
jer_lat = 31.771959
jer_lng = 35.217018


sunset_api_params = {'lat': jer_lat, 'lng': jer_lng, 'date': 'today'}
r = requests.get(url=sunset_api_url, params=sunset_api_params)
sunset_time_string = r.json()['results']['sunset']  # <-- UTC, Israel --> UTC + 2, Shabbat --> (Israel - 18 min)

sunset_time = datetime.datetime.strptime(sunset_time_string, "%H:%M:%S %p")
shabbat_time = sunset_time + datetime.timedelta(hours=2) - datetime.timedelta(minutes=18)

slack_client = WebClient(token=token)
try:
    response = slack_client.chat_postMessage(channel='#test', text="Greeting", blocks=message_blocks)
except SlackApiError as e:
    print(f"Got an error: {e.response['error']}")
