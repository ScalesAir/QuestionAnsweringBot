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

storage = MemoryStorage()

config = configparser.ConfigParser()  # создаём объекта парсера .ini
config.read("settings.ini")  # читаем конфиг

bot = Bot(token=config["BOT"]["token"])
dp = Dispatcher(bot, storage=storage)
# dp = Dispatcher(bot)
