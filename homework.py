import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv

import advanced_value as av

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
LOG_NAME_FILE = os.getenv('LOG_NAME_FILE')
bot = telegram.Bot(token=TELEGRAM_TOKEN)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
    filename=LOG_NAME_FILE,
    filemode='w')


def parse_homework_status(homework):
    """Спарсить данные объекта ревью."""
    homework_name = homework['homework_name']
    if homework['status'] == 'rejected':
        verdict = av.VERDICT['rejected']
    elif homework['status'] == 'reviewing':
        verdict = av.VERDICT['reviewing']
    else:
        verdict = av.VERDICT['default']
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """Получить данные ревью."""
    data = {
        'from_date': current_timestamp
    }
    homework_statuses = requests.get(
        av.URL_DOMASHKA,
        params=data,
        headers={'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'})
    return homework_statuses.json()


def send_message(message, bot_client):
    """Отправить сообщение в Телеграм."""
    logging.info('Send message')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    """Бот по опросу состояния ревью."""
    logging.debug('Start bot')
    current_timestamp = int(time.time())

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
            print(f'{av.BOT_ERROR}: {e}')
            time.sleep(av.TIME_SLEEP)


if __name__ == '__main__':
    main()
