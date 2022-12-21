from datetime import datetime
from data_base.sqlite_bd import find_column


async def get_date_time():
    return f'{datetime.now().strftime("%d.%m.%Y %H:%M:%S")}'


async def data_from_database_row(database_row, row):
    """
    Функция возвращает текст под индексом row из списка database_row
    применяется для получения id, имени пользователя после функции sqlite_db.find_column()
    :param database_row:
    :param row:
    :return:
    """
    for data in database_row:
        return data[row]


async def three_letters(text):
    """
    Функция ищет три буквы подряд в тексте, возвращает эти буквы(temp), через запятую и правильную фразу(w)
    :param text:
    :return:
    """
    import re
    letters = set(re.findall(r'(.)\1{2,}', text.casefold()))
    temp = ','.join(letters)
    if len(temp) > 0:
        w = 'букву'
        if len(temp) > 1:
            w = 'буквы'
        return temp, w
    else:
        return '', ''


async def get_user_name(message, id_user=0):
    """
    Функция возвращает имя пользователя с БД или first_name телеграмма
    :param id_user:
    :param message:
    :return:
    """
    if id_user == 0:
        id_user = message.from_user.id
    temp = await find_column('users', 'telegram_id', id_user)
    if len(temp) > 0:
        return await data_from_database_row(temp, 1)
    else:
        return message.from_user.first_name
