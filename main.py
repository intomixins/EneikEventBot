import os
import telebot
import requests
from dotenv import load_dotenv
from phrases import *
from apscheduler.schedulers.background import BlockingScheduler
from tzlocal import get_localzone

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

chat_id = -1001966702354


def send_event_map():
    response = requests.get('https://eneik.ge/event/telegram').json()
    mes = f'{COMMON_TEXT}\n\n'
    for event in response:
        status = True if 'subtitles' in event['description'] else False
        url = f'https://eneik.ge/event/{event["id"]}'
        date, time = event['dateStart'].split(' ')
        date = f"#{date.split('-')[2]}{DCT[date.split('-')[1]]}{date.split('-')[0]}"
        time = f"{time.split(':')[0]}:{time.split(':')[1]}"
        if status:
            mes += f'🎥{date} в {time} будет показ фильма {event["name"]}\n'
        else:
            mes += f'{date} в {time} будет {event["name"]}\n'
        mes += f'Описание: {event["description"]}\n'
        mes += f'Цена: {event["price"]} лари\n'
        mes += f'{url}\n\n'
    mes += FINISH_TEXT
    bot.send_message(chat_id, mes, reply_to_message_id=2)


sched = BlockingScheduler(timezone=get_localzone())
sched.add_job(send_event_map, 'cron', day_of_week='mon', hour=9)
sched.start()
