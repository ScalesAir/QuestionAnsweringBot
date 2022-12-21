from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from functions.message_func import reply_msg, send_msg, edit_msg
from functions.other_func import get_date_time, get_user_name
from data_base.sqlite_bd import set_bd_update, find_column, delete_line_bd_msg, delete_bd_msg
from keyboards.client_kb import create_button_inline
from handlers.admin import check_moderator
from create_bot import dp
from logs import logging

logger = logging.getLogger("app.question_lifecycle.response_message")

__all__ = ['registration_handlers_give_answer']


class FSMNew_answer(StatesGroup):
    answer = State()
    negative_answer = State()


# async def start_response_message():


@dp.callback_query_handler(Text(startswith='work:'), state=None)
async def call_worked(callback: types.CallbackQuery):
    question_id = int(callback.data.split(':')[1])
    user_id = int(callback.data.split(':')[2])
    msg_id = int(callback.data.split(':')[3])
    await FSMNew_answer.answer.set()
    state = Dispatcher.get_current().current_state()
    await edit_msg(callback.message.chat.id, msg_id, f'Вы приняли заявку №{question_id}')
    async with state.proxy() as data:
        data['user_id'] = user_id
        data['question_id'] = question_id
        data['result'] = 'y'

    # await callback.answer(f'Ответ по заявке №{question_id} отправлен', show_alert=True)
    # await FSMNew_question.question.set()
    await send_msg(callback.message, f'Напишите ответ на заявку {question_id}',
                   spec_chat_id=callback.message.chat.id)


@dp.callback_query_handler(Text(startswith='rej:'), state=None)
async def call_reject(callback: types.CallbackQuery):
    question_id = int(callback.data.split(':')[1])
    user_id = int(callback.data.split(':')[2])
    msg_id = int(callback.data.split(':')[3])
    await FSMNew_answer.answer.set()
    state = Dispatcher.get_current().current_state()
    await edit_msg(callback.message.chat.id, msg_id, f'Вы отказали заявку №{question_id}')
    async with state.proxy() as data:
        data['user_id'] = user_id
        data['question_id'] = question_id
        data['result'] = 'n'
    await send_msg(callback.message, f'Напишите причину отказа по заявке №{question_id}',
                   spec_chat_id=callback.message.chat.id)


async def create_grade_kb(question_id):
    kb = create_button_inline(5, t1='1', c1=f'grade:1:{question_id}',
                              t2='2', c2=f'grade:2:{question_id}',
                              t3='3', c3=f'grade:3:{question_id}',
                              t4='4', c4=f'grade:4:{question_id}',
                              t5='5', c5=f'grade:5:{question_id}', )
    return kb


async def answer_to_question(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        question_id = data['question_id']
        user_id = data['user_id']
        result = data['result']
    await state.finish()
    await set_bd_update('questions', 'question_id', question_id, 'answer', message.text)
    kb = create_button_inline(2, t1='Да', с1=f'snd:y:{question_id}:{user_id}:{result}',
                              t2='Изменить текст', c2=f'snd:n:{question_id}:{user_id}:{result}')
    await reply_msg(message, 'Оправить ответ?', kb)


@dp.callback_query_handler(Text(startswith='snd:'), state=None)
async def send_answer(callback: types.CallbackQuery):
    send = callback.data.split(':')[1]
    question_id = int(callback.data.split(':')[2])
    user_id = int(callback.data.split(':')[3])
    result = callback.data.split(':')[4]
    temp = await find_column('questions', 'question_id', question_id)
    text = temp[0][8]
    if send == 'y':
        await edit_msg(callback.message.chat.id, callback.message.message_id,
                       f'Ответ по заявке №{question_id} отправлен '
                       f'{await get_user_name(callback.message, user_id)}')
        if result == 'y':
            await set_bd_update('questions', 'question_id', question_id, 'time_end', await get_date_time())
            logger.info(f'{await get_date_time()} - {await get_user_name(callback.message, callback.message.chat.id)} '
                        f'ответил по заявке №{question_id}')
            await send_msg(callback.message,
                           f'{await get_user_name(callback.message, callback.message.chat.id)} '
                           f'ответил по заявке №{question_id}:'
                           f'\n{text}', spec_chat_id=user_id)
            # await state.finish()
            # await send_msg(callback.message, f'<b>Ответ по заявке №{question_id}↔ отправлен '
            #                                  f'{await get_user_name(callback.message, user_id)}</b>')
            await delete_line_bd_msg(question_id)
            kb = create_button_inline(2, t1='Да', с1=f'answer:yes:{question_id}:{callback.message.chat.id}',
                                      t2='Нет', c2=f'answer:no:{question_id}:{callback.message.chat.id}')
            await send_msg(callback.message, f'Был ли мой ответ полезным?', kb, spec_chat_id=user_id)
            # kb = await create_grade_kb(question_id)
            # await send_msg(callback.message, f'Оцените ответ', kb, spec_chat_id=user_id)
        if result == 'n':
            await send_msg(callback.message,
                           f'{await get_user_name(callback.message, callback.message.chat.id)} '
                           f'отказал заявку №{question_id} с примечанием:'
                           f'\n{text}', spec_chat_id=user_id)
            kb = create_button_inline(2, t1='Да', с1=f'answer:yes:{question_id}:{callback.message.chat.id}',
                                      t2='Нет', c2=f'answer:no:{question_id}:{callback.message.chat.id}')
            logger.info(f'{await get_date_time()} - {await get_user_name(callback.message, callback.message.chat.id)}'
                        f' отказал заявку №{question_id}')

            await send_msg(callback.message, f'Вас устраивает ответ?', kb, spec_chat_id=user_id)
    if send == 'n':
        await edit_msg(callback.message.chat.id, callback.message.message_id,
                       f'Вы решили изменить текст сообщения по заявке №{question_id}')
        await FSMNew_answer.answer.set()
        state = Dispatcher.get_current().current_state()
        await send_msg(callback.message, 'Наберите новый текст')
        async with state.proxy() as data:
            data['user_id'] = user_id
            data['question_id'] = question_id
            data['result'] = result


@dp.callback_query_handler(Text(startswith='answer:'), state=None)
async def call_answer(callback: types.CallbackQuery):
    answer = callback.data.split(':')[1]
    question_id = int(callback.data.split(':')[2])
    user_id = int(callback.data.split(':')[3])
    if answer == 'yes':
        await set_bd_update('questions', 'question_id', question_id, 'time_end', await get_date_time())
        logger.info(
            f'{await get_date_time()} - {await get_user_name(callback.message, id_user=callback.message.chat.id)} '
            f'устроил ответ по заявке №{question_id}')
        await edit_msg(callback.message.chat.id, callback.message.message_id,
                       f'Ваша заявка №{question_id} закрыта')
        kb = await create_grade_kb(question_id)
        await delete_line_bd_msg(question_id)
        await send_msg(callback.message, f'Оцените пожалуйста ответ', kb, spec_chat_id=callback.message.chat.id)

    if answer == 'no':
        edit_text = callback.message.text.replace('Вас устраивает ответ?', 'Ответ Вас не устроил')
        await edit_msg(callback.message.chat.id, callback.message.message_id, edit_text)
        await FSMNew_answer.negative_answer.set()
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data['question_id'] = question_id
            data['user_id'] = user_id
        await send_msg(callback.message, 'Напишите по какой причине Вас, не устраивает ответ.')


async def response_to_negative(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        question_id = data['question_id']
        user_id = data['user_id']
        temp = await find_column('questions', 'question_id', question_id)
        text = temp[0][8]
    moderators = await check_moderator()
    await delete_line_bd_msg(question_id)
    msg_id = list()
    await send_msg(message, 'Ваш вопрос отправлен повторно!')
    # TODO разобраться почему не используется moderator
    for moderator in moderators:
        kb = create_button_inline(2, t1='Принять в работу',
                                  c1=f"ok:{question_id}:{message.from_user.id}")
        await send_msg(message, f'<b>Пользователя {await get_user_name(message)}  '
                                f'не удовлетворил ответ {await get_user_name(message, user_id)}\n'
                                f'Текст отказа:</b>\n<i>{text}</i>\n'
                                f'<b>Причина:</b>\n<i>{message.text}</i>', spec_chat_id=user_id)
        msg = await send_msg(message, 'Принять заявку?', spec_chat_id=user_id, rm=kb)
        if msg:
            msg_id.append(str(user_id) + ',' + str(msg.message_id))
        else:
            logger.warning(f'{await get_user_name(message, user_id)} заблокировал пользователя')
    await delete_bd_msg(question_id, '|'.join(msg_id))
    await state.finish()


@dp.callback_query_handler(Text(startswith='grade:'), state=None)
async def call_grade(callback: types.CallbackQuery):
    grade = int(callback.data.split(':')[1])
    question_id = int(callback.data.split(':')[2])
    await edit_msg(callback.message.chat.id, callback.message.message_id,
                   f'Заявка №{question_id} закрыта.\nВаша оценка: {grade}')
    await set_bd_update('questions', 'question_id', question_id, 'grade', grade)
    temp = await find_column('questions', 'question_id', question_id)
    responsible_id = temp[0][7]
    await send_msg(callback.message, f'Ваш ответ удовлетворил '
                                     f'{await get_user_name(callback.message, id_user=callback.message.chat.id)} '
                                     f'с оценкой {str(grade)}\n'
                                     f'Заявка №{question_id} закрыта.', spec_chat_id=responsible_id)

    await callback.answer()


def registration_handlers_give_answer(_dp: Dispatcher):
    _dp.register_message_handler(answer_to_question, chat_type=types.ChatType.PRIVATE,
                                 state=FSMNew_answer.answer)
    _dp.register_message_handler(response_to_negative, chat_type=types.ChatType.PRIVATE,
                                 state=FSMNew_answer.negative_answer)
