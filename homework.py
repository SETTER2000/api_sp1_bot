import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv

import advanced_value as av

load_dotenv()
try:
    PRAKTIKUM_TOKEN = os.environ['PRAKTIKUM_TOKEN']
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
except Exception as e:
    logging.error(f'{av.BOT_ERROR}: {e}')


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename='main.log',
    filemode='w')


def parse_homework_status(homework):
    """Спарсить данные объекта ревью."""
    try:
        verdict = av.VERDICT.get(homework.get('status'))
        homework_name = homework.get('homework_name')
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as e:
        logging.error(f'{av.BOT_ERROR}: {e}')


def get_homework_statuses(current_timestamp):
    """Получить данные ревью."""
    try:
        data = {'from_date': current_timestamp}
        token = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
        homework_statuses = requests.get(
            av.URL_DOMASHKA,
            params=data,
            headers=token)
        return homework_statuses.json()
    except Exception as e:
        logging.error(f'{av.BOT_ERROR}: {e}')
        return {}


def send_message(message, bot_client):
    """Отправить сообщение в Телеграм."""
    logging.info('Send message')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    """Бот по опросу состояния ревью."""
    current_timestamp = int(time.time())
    try:
        bot = telegram.Bot(token=TELEGRAM_TOKEN)
        logging.debug('Start bot')
        send_message('Спасибо, что запустили меня. (bot Вася)', bot)
    except Exception as e:
        logging.error(f'{av.BOT_ERROR}: {e}')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]),
                    bot)
            current_timestamp = new_homework.get('current_date',
                                                 current_timestamp)
            time.sleep(av.TIME_SLEEP)

        except Exception as e:
            logging.error(f'{av.BOT_ERROR}: {e}')
            send_message(f'{av.BOT_ERROR}: {e}', bot)
            time.sleep(av.TIME_SLEEP)


if __name__ == '__main__':
    main()
