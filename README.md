### Описание
Telegram-бот, отправляющий статус ревью домашних работ во время обучения в Яндекс.Практикум.

### Стек технологий, использованный в проекте:

Python 3.7

REST API

Logging

OAuth

### Запуск проекта на локальной машине:
- Клонировать репозиторий и перейти в него в командной строке.
- Установить и активировать виртуальное окружение c учетом версии Python 3.7 (выбираем python не ниже 3.7):

```py -3.7 -m venv venv```

```source venv/Scripts/activate```
- Затем нужно установить все зависимости из файла requirements.txt

```python -m pip install --upgrade pip```

```pip install -r requirements.txt```
- Заполнить "секретные" данные:

```PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID```
- Запускаем homework.py


Автор в рамках учебного курса ЯП Python - Python-разработчик:

✅ Stanislav Krutskikh
