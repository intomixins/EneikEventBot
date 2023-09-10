import os
import telebot
import requests
from dotenv import load_dotenv
from phrases import *
from apscheduler.schedulers.background import BlockingScheduler
from tzlocal import get_localzone

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

chat_id = -1001966702354  # mine
# chat_id = -1001855558283  # eneik


@bot.message_handler(commands=['id'])
def get_id(message):
    print(message.message_thread_id)


def send_event_map():
    response = requests.get('https://eneik.ge/event/telegram').json()

    bot.send_message(
        chat_id,
        COMMON_TEXT,
        message_thread_id=332,
        parse_mode='html'
    )

    no_tag = ''
    DAILY = {
        '#каждый_понедельник': '',
        '#каждый_вторник': '',
        '#каждую_среду': '',
        '#каждый_четверг': '',
        '#каждую_пятницу': '',
        '#каждую_субботу': '',
        '#каждое_воскресенье': '',
    }

    for event in response:
        status = True if 'dub' in event['description'] else False
        url = f'https://eneik.ge/event/{event["id"]}'
        date, time = event['dateStart'].split(' ')
        day, month, year = (
            date.split('-')[2],
            DCT[date.split('-')[1]],
            date.split('-')[0]
        )
        if int(day) < 10:
            day = day[1]
        date = f"#{day}{month}{year}"
        time = f"{time.split(':')[0]}:{time.split(':')[1]}"
        name, description, price = (
            event["name"],
            event["description"],
            event["price"]
        )
        flag = False
        result = ''
        if status:
            result += f'🎥{date}\n{time} показ фильма <b>{event["name"]}</b>\n\n'
            result += f'Описание: {description}\n'
        else:
            result += f'{date}\n{time} <b>{event["name"]}</b>\n'
            result += f'{url}\n'
            result += f'Описание: {description}\n'
            result += f'Цена: {price} лари\n\n'
        for day_of_week in DAILY:
            if day_of_week in description:
                flag = True
                DAILY[day_of_week] += result
        if not flag:
            no_tag += result
    bot.send_photo(chat_id, open(f'photos/no_tag.png', 'rb'), reply_to_message_id=332, parse_mode='html')
    bot.send_message(chat_id, f'{no_tag}\n\n{FINISH_TEXT}', reply_to_message_id=332, parse_mode='html')
    for day_of_week in DAILY:
        if DAILY[day_of_week]:
            photo = open(f'photos/{day_of_week}.jpg', 'rb')
            bot.send_photo(chat_id, photo, f'{DAILY[day_of_week]}\n\n{FINISH_TEXT}',
                           reply_to_message_id=332, parse_mode='html')


sched = BlockingScheduler(timezone=get_localzone())
sched.add_job(send_event_map, 'cron', day_of_week='sat', hour=14)
sched.start()
