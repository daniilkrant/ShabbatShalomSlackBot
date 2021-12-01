import datetime
import os

import requests
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

sunset_api_url = "https://api.sunrise-sunset.org/json"

slack_message_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'slack_message.json')
customer_location_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shabbat_location.json')
slack_token_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.json')

with open(slack_token_file_path) as json_file:
    token = json.load(json_file)["slack_token"]

with open(slack_message_file_path) as json_file:
    message_blocks = json.load(json_file)

with open(customer_location_file_path) as json_file:
    location = json.load(json_file)
    shabbat_lat = location["lat"]
    shabbat_lng = location["lng"]


sunset_api_params = {'lat': shabbat_lat, 'lng': shabbat_lng, 'date': 'today'}
r = requests.get(url=sunset_api_url, params=sunset_api_params)
sunset_time_string = r.json()['results']['sunset']  # <-- UTC, Israel --> UTC + 2, Shabbat --> (Israel - 18 min)

sunset_time = datetime.datetime.strptime(sunset_time_string, "%H:%M:%S %p")
shabbat_time = sunset_time + datetime.timedelta(hours=2) - datetime.timedelta(minutes=18)

slack_client = WebClient(token=token)
try:
    response = slack_client.chat_postMessage(channel='#test', text="Greeting", blocks=message_blocks)
except SlackApiError as e:
    print(f"Got an error: {e.response['error']}")
