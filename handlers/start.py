from aiogram import types, Dispatcher
from functions.message_func import send_msg, answer_msg
from data_base.sqlite_bd import find_column
from functions.other_func import data_from_database_row
from handlers.registration_users import registration

from logs import logging


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
    await send_msg(message, f'Доброго времени суток! 🤗\nЯ автоматизированный помощник ОДС,\n'
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
