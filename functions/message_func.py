from create_bot import bot
from aiogram.types import ReplyKeyboardRemove
import exceptions  # Свой модуль, обработки исключений aiogram
from logs import logging

logger = logging.getLogger("app.functions.message_func")


async def edit_msg(chat_id, message_id, text, rm=''):
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


async def send_msg(message, text, rm=ReplyKeyboardRemove(), spec_chat_id=''):
    """
        Функция отправки сообщения пользователям и удаляет старые ReplyKeyboard клавиатуры
    :param message:
    :param text:
    :param rm:
    :param spec_chat_id:  # Используется, если сообщение нужно отправить определенному пользователю
    :return:
    """
    try:
        if spec_chat_id != '':
            msg = await bot.send_message(spec_chat_id, text, parse_mode='html', reply_markup=rm)
        else:
            msg = await bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=rm)
        # print(msg)
    except exceptions.CantInitiateConversation:  # TODO Проверить
        logger.warning(
            f'Бот не может начать разговор с пользователем {message.from_user.first_name}({message.from_user.id})')
        await bot.send_message(message.chat.id,
                               '<b>Бот сможет Вам ответить, как только Вы ему напишите хотя бы один раз.</b>'
                               '\n<i><b>https://t.me/CUS_HelpBot</b></i>', parse_mode='html')
    except exceptions.ChatNotFound as error_chat:
        logger.error(f'send_message Не верно указан ЧАТ! - {repr(error_chat)}')
    except exceptions.CantParseEntities as error_parse_end:
        logger.error(f'send_message Несоответствующий конечный тег - {repr(error_parse_end)}')
    except exceptions.MessageTextIsEmpty as error_TextIsEmpty:
        logger.error(f'send_message Текст сообщения пуст - {repr(error_TextIsEmpty)}')
    except exceptions.BadRequest as error_request:
        logger.error(f'send_message Неподдерживаемый режим parse_mode - {repr(error_request)}')
    except exceptions.BotBlocked as blocked:
        logger.error(f'бот был заблокирован пользователем - {repr(blocked)}')
    except Exception as error_sent_message:
        logger.error(f'send_message Неизвестная ошибка при отправке сообщения боту  {repr(error_sent_message)}')
        return None
    else:
        return msg


async def answer_msg(message, text, rm=ReplyKeyboardRemove()):
    """
    Функция отправки сообщения пользователю в ответ
    :param message:
    :param text:
    :param rm:
    :return:
    """
    try:
        await message.answer(text, parse_mode='html', reply_markup=rm)
    except exceptions.CantInitiateConversation:  # TODO Проверить
        logger.warning(
            f'Бот не может начать разговор с пользователем {message.from_user.first_name}({message.from_user.id})')
        await bot.send_message(message.chat.id,
                               '<b>Бот сможет Вам ответить, как только Вы ему напишите хотя бы один раз.</b>'
                               '\n<i><b>https://t.me/CUS_HelpBot</b></i>', parse_mode='html')
    except exceptions.ChatNotFound as error_chat:
        logger.error(f'answer_msg Не верно указан ЧАТ! - {repr(error_chat)}')
    except exceptions.CantParseEntities as error_parse_end:
        logger.error(f'answer_msg Несоответствующий конечный тег - {repr(error_parse_end)}')
    except exceptions.MessageTextIsEmpty as error_TextIsEmpty:
        logger.error(f'answer_msg Текст сообщения пуст - {repr(error_TextIsEmpty)}')
    except exceptions.BadRequest as error_request:
        logger.error(f'answer_msg Неподдерживаемый режим parse_mode - {repr(error_request)}')
    except Exception as error_sent_message:
        logger.error(f'answer_msg Неизвестная ошибка при отправке сообщения боту  {repr(error_sent_message)}')


async def reply_msg(message, text, rm=ReplyKeyboardRemove()):
    """
    Функция отправки сообщения пользователю в ответ и содержит в себе сообщение пользователя
    :param message:
    :param text:
    :param rm:
    :return:
    """
    try:
        await message.reply(text, parse_mode='html', reply_markup=rm)
    except exceptions.CantInitiateConversation:  # TODO Проверить
        logger.warning(
            f'Бот не может начать разговор с пользователем {message.from_user.first_name}({message.from_user.id})')
        await bot.send_message(message.chat.id,
                               '<b>Бот сможет Вам ответить, как только Вы ему напишите хотя бы один раз.</b>'
                               '\n<i><b>https://t.me/CUS_HelpBot</b></i>', parse_mode='html')
    except exceptions.ChatNotFound as error_chat:
        logger.error(f'reply_msg Не верно указан ЧАТ! - {repr(error_chat)}')
    except exceptions.CantParseEntities as error_parse_end:
        logger.error(f'reply_msg Несоответствующий конечный тег - {repr(error_parse_end)}')
    except exceptions.MessageTextIsEmpty as error_TextIsEmpty:
        logger.error(f'reply_msg Текст сообщения пуст - {repr(error_TextIsEmpty)}')
    except exceptions.BadRequest as error_request:
        logger.error(f'reply_msg Неподдерживаемый режим parse_mode - {repr(error_request)}')
    except Exception as error_sent_message:
        logger.error(f'reply_msg Неизвестная ошибка при отправке сообщения боту  {repr(error_sent_message)}')

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
