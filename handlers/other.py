import asyncio

from create_bot import bot, dp
import json  # Работа с json файлами, тут нужен для фильтра мата
import string  # Для выдергивания спец символом таких как '!@#$', нужно для определения маскировки мата
import random

from aiogram import types, Dispatcher
from functions.message_func import send_msg, reply_msg, answer_msg
from aiogram.dispatcher.filters import ChatTypeFilter
from functions.other_func import get_user_name, get_date_time
from handlers.admin import check_ban
from handlers.submit_request import entering_a_question
from logs import logging

logger = logging.getLogger("app.handlers.other")

__all__ = ['registration_handlers_other']


async def command_test(message: types.Message):
    """Функция регистрации Хендлеров, при этом декораторы не нужны

    :return:
    """
    try:
        if await check_ban(message.from_user.id):
            logger.warning(f'Заблокированный пользователь пишет боту:{message.text}')
            return
        user = await get_user_name(message)
        if message.from_user.id != 541261735 and message.from_user.id != 411787402:
            logger.info(f'{await get_date_time()} Пользователь {user} нажал на ТЕСТ')
            await message.delete()
            temp1 = await send_msg(message, '⚠️У Вас нет доступа к тестированию⚠️',
                                   spec_chat_id=message.from_user.id)
            temp = await send_msg(message, '🙄', rm=None, spec_chat_id=message.from_user.id)
            await asyncio.sleep(2.5)
            temp2 = await bot.edit_message_text(chat_id=message.from_user.id,
                                                message_id=temp.message_id,
                                                text='🤭')
            await asyncio.sleep(2.8)
            await bot.edit_message_text(chat_id=message.from_user.id,
                                        message_id=temp.message_id,
                                        text='🥱')
            await asyncio.sleep(3)
            await bot.delete_message(message.from_user.id, temp2.message_id)
            await asyncio.sleep(5)
            await bot.delete_message(message.from_user.id, temp1.message_id)
        else:
            await new_question(message)
    except Exception as err:
        logger.error('Ошибка теста', err)


async def send_text_private(message: types.Message):
    """Функция обрабатывает текстовые сообщения переданные телеграм Боту
        Она должна быть в коде последней.

    :param message:
    :return:
    """
    # Фильтр матов

    if await check_ban(message.from_user.id):
        logger.warning(f'Заблокированный пользователь пишет боту:{message.text}')
        return
    hello = ["Здравствуйте", "Добрый день", "Приветствую Вас"]
    random_index = random.randint(0, len(hello) - 1)
    if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')} \
            .intersection(set(json.load(open('censure.json')))) != set():
        await reply_msg(message, 'Маты запрещены')
        await message.delete()
        logger.info(f'Пользователь {await get_user_name(message)}({message.from_user.id}) написал в чат '
                    f'\"{message.text}\"')
    elif message.text.casefold() == 'привет' or message.text.casefold() == 'здравствуйте':
        await answer_msg(message, f'{hello[random_index]}, {await get_user_name(message)}!')
    elif {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')} \
            .intersection(set(json.load(open('hello.json')))) != set():
        await send_msg(message, f'👋{hello[random_index]}, <i>{await get_user_name(message)}!</i>')
        await entering_a_question(message)
        logger.info(f'У пользователя {await get_user_name(message)}({message.from_user.id}) '
                    f'есть вопрос \"{message.text}\"')
    else:
        pass
        # await reply_msg(message, f'{await get_user_name(message)}, Бот пока не знает ответ на Ваш вопрос.')
        # await entering_a_question(message)


async def send_text_goup(message: types.Message):
    pass
    # print(message.chat.id, message.from_user.id)


def registration_handlers_other(_dp: Dispatcher):
    """Функция регистрации Хендлеров, при этом декораторы не нужны

    :param _dp:
    :return:
    """
    _dp.register_message_handler(send_text_private,
                                 ChatTypeFilter(chat_type=types.ChatType.PRIVATE),
                                 content_types=['text'])  # Должна быть в самом конце. Обрабатывает сообщения в личку
    _dp.register_message_handler(send_text_goup,
                                 content_types=['text'])  # Должна быть в самом конце. Обрабатывает сообщения в личку
