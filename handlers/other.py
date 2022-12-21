import asyncio

from create_bot import bot, dialogflow, session_client, session, language_code
# import json # Работа с json файлами, тут нужен для фильтра мата
# import string # Для выдергивания спец символом таких как '!@#$', нужно для определения маскировки мата
import random

from aiogram import types, Dispatcher

from data_base import max_rowid, find_column
from functions.message_func import send_msg, answer_msg
from aiogram.dispatcher.filters import ChatTypeFilter
from functions.other_func import get_user_name, get_date_time, data_from_database_row
from handlers import registration
from handlers.admin import check_ban
from censure.censure import censure_filter

from logs import logging
from handlers.submit_request import FSMNew_question, load_text

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
            pass
    except Exception as err:
        logger.error('Ошибка теста', err)


async def send_msg_moderator(message: types.Message, text: str):
    random_text = ["Отправить Ваш вопрос модератору?", "Могу отправить Ваш вопрос модератору"]
    random_index = random.randint(0, len(random_text) - 1)
    await answer_msg(message, f'{random_text[random_index]}')
    question_id = int(await max_rowid()) + 1
    await FSMNew_question.text.set()
    state = Dispatcher.get_current().current_state()
    async with state.proxy() as data:
        data['question_id'] = question_id
        data['user_id'] = message.from_user.id,
    message.text = text
    await load_text(message, state)


async def send_text_private(message: types.Message):
    """Функция обрабатывает текстовые сообщения переданные телеграм Боту
        Она должна быть в коде последней.

    :param message:
    :return:
    """

    if await check_ban(message.from_user.id):
        logger.warning(f'Заблокированный пользователь пишет боту:{message.text}')
        return
    # Фильтр матов
    text = await censure_filter(message.text)
    temp = await find_column('users', 'telegram_id', message.from_user.id)
    telegram_id = await data_from_database_row(temp, 0)

    if not telegram_id:
        await registration(message)
        return

    # Если текст вопроса превышает 250 символов(ограничения dialogflow), тогда текст направляется модератору.
    if len(message.text) >= 250:
        await send_msg_moderator(message, text)
        return

    text_input = dialogflow.TextInput({'text': message.text, 'language_code': language_code})
    query_input = dialogflow.QueryInput({'text': text_input})  # Ввод запроса

    # hello = ["Здравствуйте", "Добрый день", "Приветствую Вас"]
    # random_index = random.randint(0, len(hello) - 1)
    # if {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')} \
    #         .intersection(set(json.load(open('censure.json')))) != set():
    #     await reply_msg(message, 'Маты запрещены')
    #     await message.delete()
    if text.find('***') >= 0:
        logger.info(f'Пользователь {await get_user_name(message)}({message.from_user.id}) написал \n'
                    f'\"{message.text}\"\nа бот заменил на: {text}')
    # elif message.text.casefold() == 'привет' or message.text.casefold() == 'здравствуйте':
    #     await answer_msg(message, f'{hello[random_index]}, {await get_user_name(message)}!')
    # elif {i.lower().translate(str.maketrans('', '', string.punctuation)) for i in message.text.split(' ')} \
    #         .intersection(set(json.load(open('hello.json')))) != set():
    #     await send_msg(message, f'👋{hello[random_index]}, <i>{await get_user_name(message)}!</i>')
    #     await entering_a_question(message)
    #     logger.info(f'У пользователя {await get_user_name(message)}({message.from_user.id}) '
    #                 f'есть вопрос \"{message.text}\"')
    response = session_client.detect_intent(  # Ответ бота
        session=session, query_input=query_input)

    if '/arranged_an_answer"' in str(response):
        print('response', response)
    # TODO Сделать возможность пользователю подтвердить что его устроил ответ.
    # kb = create_button_inline(2, t1='Да', с1=f'b_ans:yes:{question_id}:{callback.message.chat.id}',
    #                           t2='Нет', c2=f'b_ans:no:{question_id}:{callback.message.chat.id}')
    # await send_msg(callback.message, f'Был ли мой ответ полезным?', kb, spec_chat_id=user_id)
    # elif 'trigger_have_question' in str(response):
    #
    if response.query_result.fulfillment_text:  # Если ответ имеется
        await bot.send_message(message.from_user.id,
                               response.query_result.fulfillment_text)  # Отправляем его пользователю
        # print(response)
    else:  # В обратном случае
        filter_stars = text.replace('*', '').replace(' ', '')
        if len(filter_stars) < 2:
            await answer_msg(message, f'Извините, я не распознал вопроса. Только {text}')
            return

        await answer_msg(message, "Я пока не знаю ответ на Ваш вопрос.")  # Я тебя не понимаю
        # kb = create_button_inline(2, t1='да', c1=f'question_send:yes:{message.message_id}',
        #                           t2='нет', c2=f'question_send:no:{message.message_id}',)
        await send_msg_moderator(message, text)


# async def send_text_goup(message: types.Message):
#     pass
#     # print(message.chat.id, message.from_user.id)


def registration_handlers_other(_dp: Dispatcher):
    """Функция регистрации Хендлеров, при этом декораторы не нужны

    :param _dp:
    :return:
    """
    _dp.register_message_handler(send_text_private,
                                 ChatTypeFilter(chat_type=types.ChatType.PRIVATE),
                                 content_types=['text'])  # Должна быть в самом конце. Обрабатывает сообщения в личку
    # _dp.register_message_handler(send_text_goup,
    #                              content_types=['text'])  # Должна быть в самом конце. Обрабатывает сообщения в личку
