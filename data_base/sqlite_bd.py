import sqlite3
import sqlite3 as sq
from logs import logging

__all__ = ['sql_start',
           'sql_close',
           'sql_add_users',
           'find_column',
           'max_rowid',
           'sql_read',
           'set_bd_update',
           'delete_line_bd_msg',
           'sql_add_question',
           'delete_bd_msg',
           'find_no_end_questions']

logger = logging.getLogger("app.data_base.sqlite_bd")

base: sqlite3.Connection  # Определяем тип глобальной переменной base
cur: sqlite3.Cursor  # Определяем тип глобальной переменной cur


def sql_start():
    global base, cur
    try:
        base = sq.connect('database.db')
        cur = base.cursor()
        if base:
            logger.info(f'БД подключена')
            base.execute("""CREATE TABLE IF NOT EXISTS {}(
                    telegram_id INTEGER PRIMARY KEY, 
                    name TEXT,
                    phone TEXT)""".format('users'))
            base.commit()
            base.execute("""CREATE TABLE IF NOT EXISTS {}(
                                        question_id INTEGER PRIMARY KEY,
                                        users_id INTEGER,
                                        text TEXT,
                                        photos TEXT,
                                        videos TEXT,
                                        documents TEXT,
                                        time_start TEXT,
                                        responsible_id TEXT,
                                        answer TEXT,
                                        acceptance_time TEXT,
                                        time_end TEXT,
                                        grade INTEGER)""".format('questions'))
            base.commit()
            base.execute("""CREATE TABLE IF NOT EXISTS {}( 
                                                            user_id INTEGER PRIMARY KEY)""".format('ban'))
            base.commit()
            base.execute("""CREATE TABLE IF NOT EXISTS {}( 
                                                                        user_id INTEGER PRIMARY KEY)"""
                         .format('moderator'))
            base.commit()
            base.execute("""CREATE TABLE IF NOT EXISTS {}( 
                                                question_id INTEGER PRIMARY KEY,
                                                messages_id INTEGER)""".format('delete_msg'))
            base.commit()
        else:
            logger.info(f'БД не подключилась')
    except Exception as err_bd:
        logger.critical(err_bd)


async def sql_add_users(state):
    try:
        async with state.proxy() as data:
            cur.execute(f'INSERT INTO users VALUES (?, ?, ?)', tuple(data.values()))
            base.commit()
    except Exception as err_bd:
        logger.critical(err_bd)


async def find_column(table, line, search):
    try:
        temp = cur.execute(f'SELECT * FROM {table} WHERE {line} = ?', (search,)).fetchall()
        #
        return temp
    except sqlite3.Error as error:
        logger.warning("find_column - Ошибка при работе с SQLite::", error)


async def find_no_end_questions():
    try:
        table = 'delete_msg'
        temp = cur.execute(f'SELECT * FROM {table}').fetchall()
        return temp
    except sqlite3.Error as error:
        logger.warning("find_no_end_questions - Ошибка при работе с SQLite::", error)


async def max_rowid():
    temp = cur.execute(f'SELECT * FROM questions WHERE rowid = (SELECT MAX(rowid)  FROM questions)').fetchall()
    if temp:
        for ret in temp:
            return ret[0]
    else:
        return 0


async def sql_read(tabl):
    temp = cur.execute(f'SELECT * FROM {tabl}').fetchall()
    # for ret in temp:
    #     print(ret[0], ret[1], ret[2], ret[3], ret[4], ret[5])
    return temp


async def set_bd_update(table, colum_find, line_find, cell, new_date):
    """
    :param table: Название таблицы
    :param colum_find: Столбец, по данным которого будем находить ячейку. Данные которой нужно изменить.
    :param line_find: Строка, по данным которой будем находить ячейку. Данные которой нужно изменить.
    :param cell: Ячейка, которую нужно изменить.
    :param new_date: Новые данные
    """
    try:
        # bd.cursor.execute(f"""INSERT INTO requests(request_id, telegram_id, message_id,
        # application_date, application_closing_date)
        #                   # VALUES(11313, 6446464, 879797, '01.02.03', '02.02.03');""")
        cur.execute(f"Update {table} set {cell} = ? where {colum_find} = ?", (new_date, line_find,))
        base.commit()
    except sqlite3.Error as error:
        logger.warning("set_bd_update - Ошибка при работе с SQLite::", error)


async def select_list(str_list):
    """
    Функция удаляет первый символ во всех элементах списка
    """
    # print(len(str_list))
    if len(str_list) > 0:
        new_list = list()
        for i, _ in enumerate(str_list):
            new_list.append(f'{str_list[i][0]}')
        return new_list
    else:
        return list([''])


async def get_bd_column(table, column):
    try:
        # bd.cursor.execute(f"SELECT rowid, service FROM users WHERE (? in service)", ('[САСС]',))
        # bd.cursor.execute(f"SELECT telegram_id FROM users WHERE (service LIKE ?)
        # ORDER  BY service DESC", ('%[САСС]%',))
        cur.execute(f"SELECT {column} from {table}")
        result = cur.fetchall()
        # print(select_list(result))
        return await select_list(result)
    except sqlite3.Error as error:
        logger.warning("get_bd_column - Ошибка при работе с SQLite::", error)


async def sql_add_question(question_id='', users_id='',
                           text='', photos='', videos='', documents='', time_start=''):
    try:
        cur.execute("""INSERT INTO questions(question_id, users_id, text, photos, videos, documents, time_start) 
        VALUES (?, ?, ?, ?, ?, ?, ?);""",
                    (question_id, users_id, text, photos, videos,
                     documents, time_start))
        base.commit()
    except sqlite3.IntegrityError as error:
        logger.warning(f'{question_id} уже есть БД - ', error)


async def delete_bd_msg(question_id, msg_id):
    try:
        cur.execute("""INSERT INTO delete_msg(question_id, messages_id) 
        VALUES (?, ?);""",
                    (question_id, msg_id))
        base.commit()
    except Exception as error:
        logger.warning('delete_bd_msg - ', error)


async def delete_line_bd_msg(question_id):
    try:
        cur.execute('''DELETE FROM delete_msg WHERE question_id = ?''', (question_id,))
        base.commit()
    except Exception as error:
        logger.warning('delete_line_bd_msg - ', error)


def sql_close():
    cur.close()
    base.close()
    logger.info('БД закрыта')
