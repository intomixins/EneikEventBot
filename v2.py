import os
import telebot
import requests
from time import sleep
from dotenv import load_dotenv
from phrases import COMMON_TEXT, DCT
from apscheduler.schedulers.background import BlockingScheduler
from tzlocal import get_localzone

load_dotenv()

bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))

# chat_id = -1001966702354  # mine
chat_id = -1001855558283  # eneik


@bot.message_handler(commands=['id'])
def get_id(message):
    print(message.message_thread_id)


def send_event_message():
    response = requests.get('https://eneik.ge/event/telegram').json()

    bot.send_message(
        chat_id,
        COMMON_TEXT,
        message_thread_id=332,
        parse_mode='html'
    )

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
        name, description, price, image_url = (
            event["name"],
            event["description"],
            event["price"],
            event['image'],
        )
        image = f'https://eneik.ge{image_url["shortPathToImage"]}'
        result = ''
        if status:
            result += (f'🎥{date}\n{time} показ фильма <b>{event["name"]}'
                       f'</b>\n\n')
            result += f'\n{url}\n\n'
            result += f'Описание: {description}\n'
        else:
            result += f'{date}\n{time} <b>{name}</b>\n'
            result += f'{url}\n'
            result += f'Описание: {description}\n'
            result += f'Цена: {price} ₾\n\n'
        if not image:
            image = ('https://telegram.org/file/464001533/1130b/LOLHYtTvIyg.'
                     '5632468/765938e39b6572ef3c')
        bot.send_photo(
            chat_id,
            photo=image,
            caption=result,
            reply_to_message_id=332,
            parse_mode='html'
        )
        sleep(1)


sched = BlockingScheduler(timezone=get_localzone())
sched.add_job(send_event_message, 'cron', day_of_week='sat', hour=14)
sched.start()
