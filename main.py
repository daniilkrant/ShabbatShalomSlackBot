import datetime
from datetime import date
import os
import time

import requests
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(timezone="UTC")
sunset_api_url = "https://api.sunrise-sunset.org/json"

slack_message_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'slack_message.json')
shabbat_location_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'shabbat_location.json')
slack_token_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'token.json')
slack_token = str()
shabbat_message = []
shabbat_lat = float()
shabbat_lng = float()


def read_configs():
    with open(slack_token_file_path) as json_file:
        global slack_token
        slack_token = json.load(json_file)["slack_token"]

    with open(slack_message_file_path) as json_file:
        global shabbat_message
        shabbat_message = json.load(json_file)

    with open(shabbat_location_file_path) as json_file:
        global shabbat_lng
        global shabbat_lat
        location = json.load(json_file)
        shabbat_lat = location["lat"]
        shabbat_lng = location["lng"]


def schedule_get_shabbat_time():
    scheduler.add_job(get_shabbat_time, trigger='cron', day_of_week=5, hour=1, minute=1)


def get_shabbat_time():
    sunset_api_params = {'lat': shabbat_lat, 'lng': shabbat_lng, 'date': 'today'}
    r = requests.get(url=sunset_api_url, params=sunset_api_params)
    sunset_time_string = r.json()['results']['sunset']  # <-- UTC, Israel --> UTC + 2, Shabbat --> (Israel - 18 min)

    sunset_datetime = datetime.datetime.strptime(sunset_time_string, "%I:%M:%S %p")
    sunset_datetime = sunset_datetime.replace(year=date.today().year, month=date.today().month, day=date.today().day)
    shabbat_datetime = sunset_datetime + datetime.timedelta(hours=2) - datetime.timedelta(minutes=18)
    scheduler.add_job(send_shabbat_message(), trigger='date', run_date=shabbat_datetime)


def send_shabbat_message():
    slack_client = WebClient(token=slack_token)
    try:
        slack_client.chat_postMessage(channel='#test', text="Greeting", blocks=shabbat_message)
    except SlackApiError as e:
        print(f"Got an error: {e.response['error']}")


def main():
    read_configs()
    schedule_get_shabbat_time()
    try:
        while True:
            time.sleep(2)
    except(KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == '__main__':
    main()
