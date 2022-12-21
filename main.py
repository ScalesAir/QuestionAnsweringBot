"""Телеграмм Бот для ЦУС.
   Для корректной работы библиотеки aiogram v2.23.1, требуется Python 3.10.8

"""
import handlers
from aiogram.utils import executor
from create_bot import dp
from logs import logging
from functions.other_func import get_date_time
from data_base.sqlite_bd import sql_start, sql_close

logger = logging.getLogger("app.main")


async def startup(_):
    """Функция запускается вместе с Ботом
    :param _:
    :return:
    """
    logger.info(f'{await get_date_time()} Бот QuestionAnsweringBot запущен!')
    # print(f'{await get_date_time()} Бот запущен!')
    sql_start()


async def shutdown(_):
    """Функция срабатывает при завершении бота

    :param _:
    :return:
    """
    sql_close()
    logger.info(f'{await get_date_time()} Бот отключен')
    # print(f'{await get_date_time()} Бот отключен')


handlers.registration_handlers_start(dp)  # Хендлеры клиентской части
handlers.registration_handlers_registration_users(dp)  # Хендлеры регистрации пользователей FSM
# handlers.registration_handlers_client(dp)
handlers.registration_handlers_ask_question(dp)
handlers.registration_handlers_give_answer(dp)
handlers.registration_handlers_admin(dp)  # Хендлеры админской части
handlers.registration_handlers_other(dp)  # Определяем последним, поскольку обрабатывается текст

if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown, timeout=30000)
    except ConnectionError as err:  # Не удается подключиться к хосту api.telegram.org:443
        # print(f'Не удается подключиться к хосту api.telegram.org:443 ssl:default [Превышен таймаут семафора]')
        # print(repr(err))
        logger.error(err)
