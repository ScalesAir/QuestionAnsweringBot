from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from functions.message_func import answer_msg, reply_msg, send_msg
from keyboards.client_kb import create_button_reply
from data_base.sqlite_bd import sql_add_users
from functions.other_func import three_letters, get_date_time
from handlers.submit_request import entering_a_question

import random
import re
from logs import logging

logger = logging.getLogger("app.handlers.registration_users")

__all__ = ['registration_handlers_registration_users',
           'registration']


# Класс FSM регистрации
class FSMRegistration(StatesGroup):
    name = State()
    phone = State()




async def ask_for_a_phone_number(message, rt=True):
    """
    Функция создает клавиатуру, предлагающую отправить свой телефон боту.
    Используется когда пользователь ввел свой номер телефона не корректно.
    :param message:
    :return:
    """
    kb = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True,
                                   input_field_placeholder='🔓')
    reg_button = types.KeyboardButton(text="Да, конечно",
                                      request_contact=True)

    # cancel_button = types.KeyboardButton(text="↪️Отмена")
    kb.add(reg_button)
    text = ''
    if rt:
        random_text = ["Рад знакомству", "Очень рад знакомству", "Приятно познакомиться с Вами"]
        random_index = random.randint(0, len(random_text) - 1)
        text = f'{random_text[random_index]}, {message.text}\n'
    await send_msg(message, f'{text}Могу ли я использовать Ваш номер телефона для обратной связи?', rm=kb)


async def set_phone(message):
    """
    Функция определяет, ввел пользователь номер телефона или предоставил его.
    Проверяет номер телефона на соответствие стандарту и возвращает его.
    :param message:
    :return:
    """
    if message.text and message.text != '':
        await answer_msg(message, '<b>Ввод номера телефона не доступен⚠️</b>')
        await ask_for_a_phone_number(message, False)
        return ''
    try:
        msg = message.contact.phone_number
        msg = msg.replace(' ', '')
        if len(msg) == 11:
            msg = '+' + msg
        # print(f'phone auto {msg}')
        return msg.strip()
    except Exception as error:
        logger.error(f'Ошибка отработана', error)


# async def set_directorate(message):
#     if message.text and message.text[0] != '/':
#         set_bd_update('users', 'telegram_id', message.from_user.id, 'directorate', message.text.strip())
#         print(f'directorate {message.text}')
#     # delete_msg(message.chat.id, mid.message_id)
#     else:
#         await answer_msg(message, f'<b>Вы ввели не соответствующие данные!\n🧰 Выберите свою дирекцию</b>')


async def cancel_fsm(message: types.Message, state: FSMContext):
    """
    Функция отмены FSM регистрации.
    Если пользователь ответит "отмена" или нажмет на клавишу "отмена".
    :param message:
    :param state:
    :return:
    """
    current_state = await state.get_state()
    if current_state is None:
        return
    cancel = ["Отмена❗", "Хорошо❗️", "Ок❗", "Сделано❗", "Как скажете❗️"]
    random_index = random.randint(0, len(cancel) - 1)
    await reply_msg(message, cancel[random_index])
    await state.finish()


async def registration(message: types.Message):
    await FSMRegistration.name.set()
    kb = await create_button_reply(1, '↪️Отмена')
    random_text = ["Могу ли я узнать, как Вас зовут", "Как я могу к Вам обращаться"]
    random_index = random.randint(0, len(random_text) - 1)
    await send_msg(message, f'{random_text[random_index]}?\n'
                            f'(введите ФИО)', kb, spec_chat_id=message.from_user.id)


async def load_user_name(message: types.Message, state: FSMContext):
    """
    Функция проверяет введенные фамилию и имя на соответствие стандартам и если True просит выбрать дирекцию.
    :param message:
    :param state:
    :return:
    """
    temp, w = await three_letters(message.text)
    spaces_count = len(message.text.split(' '))
    if re.search(r'[^а-яА-Я ]', message.text):
        await answer_msg(message, '<b>Используйте кириллицу без специальных символов⚠️</b>')
        await registration(message)
        return
    elif len(temp) > 0:
        await answer_msg(message, f'<b>Вы ввели {w} "{temp}" три раза подряд"⚠️</b>')
        await registration(message)
        return
    elif message.text.casefold() == 'фамилия':
        await answer_msg(message, '<b>Вы ввели слово "фамилия"👍</b>')
        await registration(message)
        return
    elif message.text.casefold() == 'имя':
        await answer_msg(message, '<b>Вы ввели слово "имя"👍</b>')
        await registration(message)
        return
    elif spaces_count < 2:
        await answer_msg(message, '<b>Вы ввели одно слово⚠️\n'
                                  'для ФИО это слишком мало</b>')
        await registration(message)
        return
    elif spaces_count > 3:
        await answer_msg(message, f'<b>Вы ввели {spaces_count} слова\n'
                                  f'Используйте пожалуйста "-" в двойном имени или фамилии</b>')
        await registration(message)
        return
    elif len(message.text) > 30:
        await answer_msg(message, '<b>Слишком много букв⚠️</b>')
        await registration(message)
        return
    elif len(message.text) <= 6:
        await answer_msg(message, '<b>К сожалению, я не встречал на столько короткие ФИО⚠️</b>')
        await registration(message)
        return

    async with state.proxy() as data:
        data['telegram_id'] = message.from_user.id
        data['name'] = message.text
    await FSMRegistration.next()
    await ask_for_a_phone_number(message)


async def load_user_phone(message: types.Message, state: FSMContext):
    """
    Если указанный номер телефона соответствует стандарту, записываем все данные из FSM state В БД
    и пишем об успешной регистрации.
    :param message:
    :param state:
    :return:
    """
    phone = await set_phone(message)
    if phone == '':
        await FSMRegistration.phone.set()
        return
    async with state.proxy() as data:
        data['phone'] = phone
    await sql_add_users(state)
    await state.finish()
    await answer_msg(message, f'Вы предоставили номер: {phone}')
    logger.info(f'{await get_date_time()} Пользователь {data["name"]} зарегистрировался')
    await entering_a_question(message)


def registration_handlers_registration_users(dp: Dispatcher):
    """
    Используется вместо декораторов вызова функций.
    :param dp:
    :return:
    """
    # dp.register_message_handler(contact, content_types=['photo'], state=FSMAdmin.photo)
    dp.register_message_handler(cancel_fsm, chat_type=types.ChatType.PRIVATE,
                                state="*", commands=['отмена', 'cancel'])
    dp.register_message_handler(cancel_fsm, Text(equals='отмена', ignore_case=True),
                                chat_type=types.ChatType.PRIVATE, state="*")
    dp.register_message_handler(load_user_name, chat_type=types.ChatType.PRIVATE,
                                state=FSMRegistration.name)
    dp.register_message_handler(load_user_phone, chat_type=types.ChatType.PRIVATE,
                                content_types=types.ContentType.CONTACT, state=FSMRegistration.phone)
    dp.register_message_handler(load_user_phone, chat_type=types.ChatType.PRIVATE,
                                state=FSMRegistration.phone)
    # dp.register_message_handler(load_user_phone, state=FSMRegistration.phone)
