from aiogram import types, Dispatcher
from functions.message_func import send_msg, answer_msg
from data_base.sqlite_bd import find_column
from functions.other_func import data_from_database_row
from handlers.registration_users import registration

from logs import logging
import datetime

logger = logging.getLogger("app.handlers.start")

__all__ = ['registration_handlers_start',
           'welcome']


async def welcome(message: types.Message):
    """Функция срабатывает если передать телеграм Боту команды /start или /help

    :param message:
    :return:
    """
    await message.delete()
    temp = await find_column('users', 'telegram_id', message.from_user.id)
    telegram_id = await data_from_database_row(temp, 0)

    times_of_day = 'Доброго времени суток'
    time_now = datetime.datetime.now().time()
    morning = datetime.time(5, 0, 0, 0)
    day = datetime.time(11, 0, 0, 0)
    evening = datetime.time(16, 0, 0, 0)
    night = datetime.time(23, 0, 0, 0)
    if (time_now > night) or (time_now < morning):
        times_of_day = 'Доброй ночи'
    if (time_now > morning) and (time_now < day):
        times_of_day = 'Доброе утро'
    if (time_now > day) and (time_now < evening):
        times_of_day = 'Добрый  день'
    if (time_now > evening) and (time_now < night):
        times_of_day = 'Добрый  вечер'

    # d1 = datetime.timedelta(hours=time_now.hour)
    # d2 = datetime.timedelta(hours=morning.hour, minutes=morning.minute, seconds=morning.second)

    await send_msg(message, f'{times_of_day}! 🤗\nЯ автоматизированный помощник ОДС,\n'
                            f'мой функционал ещё в стадии разработки и будет развиваться по мере общения с людьми.',
                   spec_chat_id=message.from_user.id)
    if not telegram_id:
        await registration(message)
    else:
        pass
        await answer_msg(message, 'Чем я могу Вам помочь?')
        # await entering_a_question(message)


def registration_handlers_start(_dp: Dispatcher):
    """Функция регистрации Хендлеров, при этом декораторы не нужны

    :param _dp:
    :return:
    """

    _dp.register_message_handler(welcome, commands=['start', 'help'])
