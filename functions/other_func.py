from datetime import datetime
from aiogram import types


from data_base.sqlite_bd import find_column


async def get_date_time() -> str:
    """
    Функция возвращает дату и время в формате: день.месяц.год часов:минут:секунд
    :return:
    """
    return f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'


async def data_from_database_row(database_row: list, row: int):
    """
    Функция возвращает текст под индексом row из списка database_row
    применяется для получения id, имени пользователя после функции sqlite_db.find_column()
    :param database_row: тип List. Содержит данные о пользователе (id,ФИО,номер телефона)
    :param row: тип int. Содержит индекс под которым нужно вернуть данные из списка.
    :return: Возвращает текст под индексом "row" из списка "database_row". Может вернуть результат разных типов.
    """
    for data in database_row:
        return data[row]


async def three_letters(text: str) -> tuple[str, str]:
    """
    Функция ищет три буквы подряд в тексте, возвращает эти буквы(three_letters), через запятую и правильную фразу(w)
    :param text: Текст в котором ищем более трех одинаковых букв. Которые стоят в тексте друг за другом.
    :return: Возвращаем буквы, которые попали под фильтр.(str) и окончание одно из: "букву", "буквы" (str)
    В случае, если совпадений нет, возвращаем два пустых параметра.
    """
    import re
    letters = set(re.findall(r'(.)\1{2,}', text.casefold()))
    three_letter = ','.join(letters)
    if len(three_letter) > 0:
        w = 'букву'
        if len(three_letter) > 1:
            w = 'буквы'
        return three_letter, w
    else:
        return '', ''


async def get_user_name(message: types.Message, id_user: int = 0) -> str:
    """
    Функция возвращает имя пользователя с БД или first_name телеграмма.
    Возвращает имя по id указанном в message.from_user.id. Если указан id_user, то по нему.
    :param id_user: id пользователя в телеграмм (не обязательный параметр)
    :param message: Сообщение types.Message
    :return: Возвращает имя пользователя. (str)
    """
    if id_user == 0:
        id_user = message.from_user.id
    user = await find_column('users', 'telegram_id', id_user)
    if len(user) > 0:
        return await data_from_database_row(user, 1)
    else:
        return message.from_user.first_name
