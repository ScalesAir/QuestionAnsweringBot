from create_bot import bot
from aiogram import types
from aiogram.types import ReplyKeyboardRemove
import exceptions  # Свой модуль, обработки исключений aiogram
from logs import logging
import traceback

logger = logging.getLogger("app.functions.message_func")


async def edit_msg(chat_id: int, message_id: int, text: str, rm: str = ''):
    """
    Функция редактирования отправленных ранее сообщений
    :param chat_id: Чат в котором необходимо изменить сообщение
    :param message_id: id сообщение которое необходимо изменить
    :param text: Новый текст сообщения
    :param rm: reply_markup (по умолчанию пустой параметр)
    :return Возвращает types.Message сообщения:
    """
    try:
        if rm != '':
            return await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                               text=text, parse_mode='html', reply_markup=rm)
        else:
            return await bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                               text=text, parse_mode='html')
    except exceptions.BotBlocked as blocked:
        logger.warning(f'бот был заблокирован пользователем - {repr(blocked)}')
        return None
    except Exception as error:
        # Определяем откуда был вызов функции
        stack = traceback.extract_stack()
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - edit_msg:{error}')
        return None

async def bot_could_not_write(message: types.Message):
    """
    По правилам телеграмм. Бот не может писать пользователям, которые ему ни разу не писали.
    Данное сообщение придет только в случае, если боту писали с общего чата или группы где администратором является бот.
    В данном случе, эта функция бесполезна. Потому, что боту пишут напрямую. Но функцию оставил, на случай фос мажора.
    :param message: Сообщение types.Message
    :return: None
    """
    await send_msg(message.chat.id,
                   '<b>Бот сможет Вам ответить, как только Вы ему напишите хотя бы один раз.</b>'
                   '\n<i><b>https://t.me/CUS_HelpBot</b></i>')


async def send_msg(message: types.Message, text: str, rm=ReplyKeyboardRemove(), spec_chat_id: int = 0):
    """
        Функция отправки сообщения пользователям и удаляет старые ReplyKeyboard клавиатуры
    :param message: types.Message сообщение
    :param text: Текст сообщения
    :param rm: reply_markup (если параметр не указать, то: ReplyKeyboardRemove() - удаление клавиатуры)
    :param spec_chat_id:  # Используется, если сообщение нужно отправить определенному пользователю
    :return возвращает types.Message сообщения:
    """
    try:
        if spec_chat_id != 0:
            msg = await bot.send_message(spec_chat_id, text, parse_mode='html', reply_markup=rm)
        else:
            msg = await bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=rm)
        return msg

    except exceptions.CantInitiateConversation:
        logger.warning(
            f'Бот не может начать разговор с пользователем {message.from_user.first_name}({message.from_user.id})')
        await bot_could_not_write(message)
    except Exception as error:
        # Определяем откуда был вызов функции
        stack = traceback.extract_stack()
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - send_msg:{error}')
        # TODO Проверить есть ли необходимость возвращать None
        return None
    # else:


async def answer_msg(message: types.Message, text: str, rm=ReplyKeyboardRemove()):
    """
    Функция отправки сообщения пользователю в ответ
    :param message: types.Message сообщение
    :param text: Текст сообщения
    :param rm: reply_markup (если параметр не указать, то: ReplyKeyboardRemove() - удаление клавиатуры)
    :return: None
    """
    # Определяем откуда был вызов функции
    stack = traceback.extract_stack()
    try:
        await message.answer(text, parse_mode='html', reply_markup=rm)
    except exceptions.CantInitiateConversation:
        logger.warning(
            f'Бот не может начать разговор с пользователем {message.from_user.first_name}({message.from_user.id})')
        await bot_could_not_write(message)
    except exceptions.ChatNotFound as error_chat:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'answer_msg Не верно указан ЧАТ! - {repr(error_chat)}')
    except exceptions.CantParseEntities as error_parse_end:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'answer_msg Несоответствующий конечный тег - {repr(error_parse_end)}')
    except exceptions.MessageTextIsEmpty as error_TextIsEmpty:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'answer_msg Текст сообщения пуст - {repr(error_TextIsEmpty)}')
    except exceptions.BadRequest as error_request:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'answer_msg Неподдерживаемый режим parse_mode - {repr(error_request)}')
    except Exception as error_sent_message:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'answer_msg Неизвестная ошибка при отправке сообщения боту  {repr(error_sent_message)}')


async def reply_msg(message, text, rm=ReplyKeyboardRemove()):
    """
    Функция отправки сообщения пользователю в ответ и содержит в себе сообщение пользователя
    :param message: types.Message сообщение
    :param text: Текст сообщения
    :param rm: reply_markup (если параметр не указать, то: ReplyKeyboardRemove() - удаление клавиатуры)
    :return: None
    """
    # Определяем откуда был вызов функции
    stack = traceback.extract_stack()
    try:
        await message.reply(text, parse_mode='html', reply_markup=rm)
    except exceptions.CantInitiateConversation:
        logger.warning(
            f'Бот не может начать разговор с пользователем {message.from_user.first_name}({message.from_user.id})')
        await bot_could_not_write(message)
    except exceptions.ChatNotFound as error_chat:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'reply_msg Не верно указан ЧАТ! - {repr(error_chat)}')
    except exceptions.CantParseEntities as error_parse_end:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'reply_msg Несоответствующий конечный тег - {repr(error_parse_end)}')
    except exceptions.MessageTextIsEmpty as error_TextIsEmpty:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'reply_msg Текст сообщения пуст - {repr(error_TextIsEmpty)}')
    except exceptions.BadRequest as error_request:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'reply_msg Неподдерживаемый режим parse_mode - {repr(error_request)}')
    except Exception as error_sent_message:
        logger.error(f'{stack[-2][2]} строка {stack[-2][1]} - '
                     f'reply_msg Неизвестная ошибка при отправке сообщения боту  {repr(error_sent_message)}')

# async def delete_msg(chat_id, msg, i=0):
#     try:
#         await bot.delete_message(chat_id, msg - i)
#     except Exception as error:
#         pass
# print(f'Ошибка  {error}')

# async def register_next_step(msg, function, *param):
#     try:
#         await dp.register_message_handler(msg, function, *param)
#     except Exception as error:
#         print(f'Ошибка отработана', error)
#     finally:
#         pass
