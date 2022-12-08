from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from functions.message_func import answer_msg, send_msg
from functions.other_func import get_date_time, get_user_name
from keyboards.client_kb import create_button_inline
from data_base.sqlite_bd import max_rowid
from logs import logging
import random

logger = logging.getLogger("app.handlers.client")

# __all__ = ['registration_handlers_client',
#            'entering_a_question']
#

# class FSMQuestions(StatesGroup):
#     question = State()
#
# async def entering_a_question(message: types.Message):
#     random_text = ["Можете задать мне свой вопрос.", "Подскажите, чем я могу помочь?",
#                    "Подскажите, чем я могу быть полезен?"]
#     random_index = random.randint(0, len(random_text) - 1)
#     await answer_msg(message, f'{random_text[random_index]}')
#     question_id = int(await max_rowid()) + 1
#     await FSMQuestions.question.set()
#     state = Dispatcher.get_current().current_state()
#     async with state.proxy() as data:
#         data['question_id'] = question_id
#         data['user_id'] = message.from_user.id
#

# async def waiting_for_a_question(message: types.Message, state: FSMContext):
#     user_data = await state.get_data()
#     print(user_data)
#     await answer_msg(message, f'{await get_user_name(message)}, Ваш вопрос ')
#     kb = await create_button_inline(2, t1='dfsdf', c1='Ответить')
#     await send_msg(message, message.text, spec_chat_id=message.from_user.id)
#



# def registration_handlers_client(_dp: Dispatcher):
#     """Функция регистрации Хендлеров, при этом декораторы не нужны
#
#     :param _dp:
#     :return:
#     """
#     _dp.register_message_handler(waiting_for_a_question, chat_type=types.ChatType.PRIVATE,
#                                  state=FSMQuestions.question)

