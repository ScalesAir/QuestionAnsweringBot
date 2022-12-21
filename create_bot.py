"""
Буферный пакет, содержит в себе класс bot и Dispatcher dp, чтобы использовать из в других модулях без ошибки
цикличного импортирования.
Токен телеграмм бота подтягивается с файла settings.ini по ключу "BOT"
storage - используется для машины состояния. Хранит данные в оперативной памяти.
"""

from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import configparser  # импортируем библиотеку для работы с .ini
import os  # Модуль для работы с операционной сис-мой
from google.cloud import dialogflow  # Модуль DialogFlow

# Относительный путь к json файлу приват-ключа
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "ods-dialogflow-ydix-a15c3382383c.json"

session_client = dialogflow.SessionsClient()  # Сессия клиента
project_id = 'ods-dialogflow-ydix'  # id проекта берём с json файла
session_id = 'sessions'  # Указываем любое значение, в моём случае "sessions"
language_code: str = 'ru'  # Язык русский
session = session_client.session_path(project_id, session_id)  # Объявляем сессию по id проекта и id сессии

storage = MemoryStorage()

config = configparser.ConfigParser()  # создаём объекта парсера .ini
config.read("settings.ini")  # читаем конфиг

bot = Bot(token=config["BOT"]["token"])
dp = Dispatcher(bot, storage=storage)
# dp = Dispatcher(bot)
