from aiogram.types import ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton
from logs import logging

logger = logging.getLogger("app.keyboards.client_kb")

__all__ = ['create_button_inline',
           'create_button_reply']


def create_button_inline(row, text='', callback='', **data):
    """
    Функция создает объект, который содержит в себе n количество InlineKeyboardMarkup кнопок.
    Пример использования:
    create_button_inline(2, text1='текст', callback1='otvet',
                            text2='Задать вопрос', callback2='ask_question',
                            text3='ла ла ла', callback3='check_your_details')
    Передавать можно динамическое количество text и callback.
    :param row: количество кнопок в сроке.
    :param text: Текст для отдельной кнопки
    :param callback: Ответ для отдельной кнопки
    :param data: Кортеж со списком в котором в аргументах содержится текст и ответ для кнопок.
    :return: Возвращает объект kb, который содержит в себе информацию о создаваемых кнопках.
    """
    # print("\nData type of argument: ", type(data))
    i = 0  # Счетчик. Нужен чтобы в последовательном списке получить text затем callback_data и так до конца списка.
    text0 = ''  # Создаем пустую переменную text
    btn = list()  # Создаем пустой список
    kb = InlineKeyboardMarkup(row_width=row)  # Создаем объект kb с количеством кнопок в строке
    if text != '':
        kb.add(InlineKeyboardButton(text=text, callback_data=callback))
    for key, value in data.items():
        match i:
            case 0:  # Получаем текст кнопки
                i = i + 1
                text0 = value  # Получаем text кнопки
            case 1:  # Получаем callback_data кнопки и формируем список кнопок
                callback0 = value  # Получаем callback_data кнопки
                btn.append(InlineKeyboardButton(text=text0, callback_data=callback0))  # Добавляем кнопку в список.
                i = 0  # обнуляем счетчик.

    kb.add(*btn)  # Добавляем в объект kb все кнопки со списка btn
    return kb  # Возвращаем объект kb для создания InlineKeyboardMarkup кнопок


async def create_button_reply(row_width, *btn, text='', text1=''):
    """
    Функция создает объект, который содержит в себе n количество ReplyKeyboardMarkup кнопок.

    :param text1:
    :param row_width: Количество кнопок в строке
    :param btn:
    :param text: Текст
    :return:
    """

    kb = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True, selective=False, one_time_keyboard=False)
    if text != '' and text1 == '':
        kb.add(text)
    if text == '' and text1 != '':
        kb.add(text1)
    if text != '' and text1 != '':
        kb.row(text, text1)
    btn = [*btn]
    kb.add(*btn)
    return kb
