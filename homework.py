import os
import telegram
from http import HTTPStatus
from dotenv import load_dotenv
import requests
import logging
import sys
import time
import exceptions


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """"Отправка сообщения в Telegram чат"""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except exceptions.SendMessageException:
        logger.error('Cбой при отправке сообщения в Telegram')
        raise exceptions.SendMessageException(
            'Cбой при отправке сообщения в Telegram'
        )
    return


def get_api_answer(current_timestamp):
    """"Отправка запросf к эндпоинту API-сервиса"""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
    except exceptions.APIAnswerException as error:
        logger.error(f'Ошибка при запросе к основному API: {error}')
        raise exceptions.APIAnswerException(
            f'Ошибка при запросе к основному API: {error}'
        )
    if response.status_code != HTTPStatus.OK:
        logger.error(f'Ошибка в работе API кода {response.status_code}')
        raise exceptions.APIAnswerException(
            f'Ошибка в работе API кода {response.status_code}'
        )
    return response.json()


def check_response(response):
    """"Проверка ответа API на корректность"""
    try:
        homework_list = response['homeworks']
    except KeyError as error:
        raise exceptions.CheckAPIException(f'Ошибка доступа по ключу {error}')
    if homework_list is None:
        raise exceptions.CheckAPIException('Списка домашних заданий нет')
    if not isinstance(homework_list, list):
        raise exceptions.CheckAPIException(
            'Ответ от API не является списком')
    if len(homework_list) == 0:
        raise exceptions.CheckAPIException(
            'Домашнего задания нет за данный промежуток времени')
    return homework_list


def parse_status(homework):
    """"Извлечение из информации о конкретной домашней работе"""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        raise KeyError(
            'Отсутствует название домашней работы'
        )
    if homework_status is None:
        raise exceptions.ParseStatusException(
            'Отсутствует статус домашней работы'
        )
    verdict = HOMEWORK_STATUSES[homework_status]
    if verdict is None:
        raise exceptions.ParseStatusException(
            'Статус домашней работы неизвестен'
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """"Проверка доступности переменных окружения"""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        logger.critical('Отсутствует один или более токен.')
        raise exceptions.CheсkTokensException(
            'Отсутствует один или более токен.'
        )
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework_list = check_response(response)
            current_timestamp = response.get('current_date')
            if len(homework_list) > 0:
                homework = homework_list[0]
                message = parse_status(homework)
                send_message(bot, message)
                logger.info('Сообщение отправлено')
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(f'Сбой в работе программы: {error}')
            send_message(bot, message)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
