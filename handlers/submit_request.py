import asyncio

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from functions.message_func import answer_msg, reply_msg, send_msg, edit_msg
from functions.other_func import get_date_time, get_user_name
from data_base.sqlite_bd import find_column, \
    sql_add_question, delete_bd_msg, max_rowid, set_bd_update, sql_read
from keyboards.client_kb import create_button_reply, create_button_inline
from create_bot import bot, dp
# from question_lifecycle.response_message import start_response_message
from logs import logging
import random

logger = logging.getLogger("app.question_lifecycle.submit_request")

__all__ = ['registration_handlers_ask_question',
           'entering_a_question',
           'dialog_question',
           'FSMNew_question',
           'load_text']


# Класс FSM отправки вопроса на нужную службу
class FSMNew_question(StatesGroup):
    text = State()
    send = State()
    media = State()


async def dialog_question(callback: types.CallbackQuery):
    send = callback.data.split(':')[1]
    callback.message.message_id = callback.data.split(':')[2]
    if send == 'yes':
        question_id = int(await max_rowid()) + 1
        await FSMNew_question.text.set()
        state = Dispatcher.get_current().current_state()
        async with state.proxy() as data:
            data['question_id'] = question_id
            data['user_id'] = callback.message.chat.id
        await load_text(callback.message, state)
    await callback.message.delete()
    await callback.answer()


async def entering_a_question(message: types.Message):
    random_text = ["Можете задать мне свой вопрос.", "Подскажите, чем я могу помочь?",
                   "Подскажите, чем я могу быть полезен?"]
    random_index = random.randint(0, len(random_text) - 1)
    await answer_msg(message, f'{random_text[random_index]}')
    question_id = int(await max_rowid()) + 1
    await FSMNew_question.text.set()
    state = Dispatcher.get_current().current_state()
    async with state.proxy() as data:
        data['question_id'] = question_id
        data['user_id'] = message.from_user.id


# async def waiting_for_a_question(message: types.Message, state: FSMContext):
#     user_data = await state.get_data()


async def create_media_group(photos, videos):
    media = types.MediaGroup()
    if photos:
        for data in photos:
            photo = data.split('|')[0]
            caption = data.split('|')[1]

            if caption != 'None' and caption != '':
                media.attach_many(types.InputMediaPhoto(photo, caption=caption, parse_mode='html'))
                # caption = ''
            else:
                media.attach_many(types.InputMediaPhoto(photo))
    if videos:
        for data in videos:
            video = data.split('|')[0]
            caption = data.split('|')[1]
            if caption != 'None' and caption != '':
                media.attach_many(types.InputMediaVideo(video, caption=caption, parse_mode='html'))
                # caption = ''
            else:
                media.attach_many(types.InputMediaVideo(video))
    return media
    # await bot.send_media_group(message.from_user.id, media)


async def create_document_group(documents):
    doc = types.MediaGroup()
    if documents:
        for data in documents:
            document = data.split('|')[0]
            caption = data.split('|')[1]
            if caption != 'None' and caption != '':
                doc.attach_many(types.InputMediaDocument(document, caption=caption, parse_mode='html'))
                # caption = ''
            else:
                doc.attach_many(types.InputMediaDocument(document))
    return doc
    # await bot.send_media_group(message.from_user.id, doc)


# async def back_fsm(message: types.Message, state: FSMContext):
#     if await FSMContext.get_state(state) == 'FSMNew_question:category':
#         await new_question(message)
#     if await FSMContext.get_state(state) == 'FSMNew_question:text':
#         async with state.proxy() as data:
#             directorate_id = data['directorate_id']
#         temp = await sql_read_categories(directorate_id)
#         kb = await create_button_reply(2, *temp, text='Отмена', text1='Назад')
#         await reply_msg(message, '<b>Выберите категорию вопроса</b>', kb)
#         await FSMNew_question.category.set()


async def bd_add_bot_question(message: types.Message, answer: str):
    # await FSMNew_question.send.set()
    # state = Dispatcher.get_current().current_state()
    user_id = message.from_user.id
    rowid = int(await max_rowid()) + 1
    await sql_add_question(rowid,
                           int(user_id),
                           str(message.text),
                           str(None),
                           str(None),
                           str(None),
                           str(await get_date_time()))
    await set_bd_update('questions', 'question_id', rowid, 'responsible_id', str('bot'))
    await set_bd_update('questions', 'question_id', rowid, 'answer', answer)
    await set_bd_update('questions', 'question_id', rowid, 'acceptance_time', str(await get_date_time()))
    kb = create_button_inline(2, t1='Да', с1=f'answer:yes:{rowid}:bot',
                              t2='Нет', c2=f'answer:no:{rowid}:bot')
    await answer_msg(message, f'Был ли мой ответ полезным?', kb)


async def bd_add_question(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    rowid = int(await max_rowid()) + 1
    async with state.proxy() as data:
        data[rowid] = rowid
    await sql_add_question(rowid,
                           int(user_data.get('user_id')),
                           str(user_data.get('text')),
                           str(user_data.get('photos')),
                           str(user_data.get('videos')),
                           str(user_data.get('documents')),
                           str(await get_date_time()))
    users = list()
    moderators = await sql_read('moderator')
    for moderator in moderators:
        users.append(moderator[0])
    await set_bd_update('questions', 'question_id', rowid, 'time_end', '')
    text = f"Вам поступила заявка №{rowid} от {await get_user_name(message, user_data.get('user_id'))}:" \
           f"\n{user_data.get('text')}"
    media = None
    doc = None

    if user_data.get('photos') or user_data.get('videos'):
        media = await create_media_group(user_data.get('photos'), user_data.get('videos'))

    if user_data.get('documents'):
        doc = await create_document_group(user_data.get('documents'))
    kb = create_button_inline(2, t1='Принять в работу',
                              c1=f"ok:{rowid}:{user_data.get('user_id')}")
    msg_id = list()
    # if not user_data.get('photos') and not user_data.get('videos') and not user_data.get('documents'):
    #     text = caption
    for id_user in users:
        # print(type(id_user), id_user, type(message.from_user.id), message.from_user.id)
        if id_user != str(message.from_user.id) or id_user == str(1621516433) or id_user == str(5412617350):
            if media:
                # await types.ChatActions.upload_photo()
                await bot.send_media_group(id_user, media=media)
            if doc:
                await bot.send_media_group(id_user, media=doc)
            # if text != '':  # Если есть (фото или видео) и документ, то текст оправить отдельно
            await send_msg(message, text, spec_chat_id=id_user)
            msg = await send_msg(message, 'Принять заявку?', spec_chat_id=id_user, rm=kb)
            if msg:
                msg_id.append(str(id_user) + ',' + str(msg.message_id))
            else:
                logger.warning(f'{await get_user_name(message, id_user)} заблокировал пользователя')
    await delete_bd_msg(rowid, '|'.join(msg_id))

    logger.info(
        f"{await get_date_time()} - {await get_user_name(message, user_data.get('user_id'))} создал заявку №{rowid}")
    await answer_msg(message, f'Ваша заявка №{rowid} зарегистрирована\nОжидайте ответ')
    #
    #     await sent_message(id_user, )


# @dp.callback_query_handler(text='ask_question')
# async def cm_ask_question(callback: types.CallbackQuery):
#     await new_question(callback.message)
#     await callback.answer()


# async def new_question(message: types.Message):
#     # await message.delete()
#     await FSMNew_question.direction.set()
#     kb = await get_directorates_kb()
#     smiley = ["📕", "📘", "📗", "📙"]
#     random_index = random.randint(0, len(smiley) - 1)
#     await send_msg(message, f'<b>{smiley[random_index]}Выберите направление вопроса</b>', kb,
#                    spec_chat_id=message.chat.id)
#


@dp.callback_query_handler(text='clear', state=FSMNew_question.send)
async def cm_edit_text(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    if user_data.get('photos'):
        user_data.pop('photos')
    if user_data.get('videos'):
        user_data.pop('videos')
    if user_data.get('documents'):
        user_data.pop('documents')
    await state.set_data(user_data)
    # user_data = await state.get_data()
    await FSMNew_question.text.set()
    await edit_msg(callback.message.chat.id, callback.message.message_id, f'Вы решили изменить текст вопроса')
    kb = await create_button_reply(2, text='Отмена', text1='Назад')
    await reply_msg(callback.message, 'Введите новый текст вопроса\n'
                                      '(при необходимости добавьте фото, видео или документ)', kb)


async def load_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        data['user_id'] = message.from_user.id
    user_data = await state.get_data()
    await FSMNew_question.send.set()
    await state.set_data(user_data)

    media = None
    doc = None

    if user_data.get('photos') or user_data.get('videos'):
        media = await create_media_group(user_data.get('photos'), user_data.get('videos'))

    if user_data.get('documents'):
        doc = await create_document_group(user_data.get('documents'))

    if media:
        await types.ChatActions.upload_photo()
        await bot.send_media_group(message.from_user.id, media=media)
    if doc:
        await bot.send_media_group(message.from_user.id, media=doc)
    msg = await send_msg(message, '.')
    await msg.delete()
    await send_msg(message, f'Ваш вопрос:\n{message.text}')

    kb = create_button_inline(2, t1='Очистить',
                              c1='clear', t2='Добавить вложение', c2='add_media',
                              t3='Отмена', с3='cancel', text='Отправить', callback='send_msg')
    # kb = await create_button_reply(2, 'Отмена', 'Назад', text='Отправить')
    await send_msg(message, 'Отправить вопрос?', kb)


@dp.callback_query_handler(text='add_media', state=FSMNew_question.send)
async def cm_add_media(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    kb = create_button_inline(1, t1='Продолжить', c2='continue')
    await edit_msg(callback.message.chat.id, callback.message.message_id, 'Добавьте нужные вложения\n'
                                                                          'и нажмите кнопку "Продолжить"', kb)
    await FSMNew_question.media.set()
    await state.set_data(user_data)


@dp.callback_query_handler(text='continue', state=FSMNew_question.media)
async def cm_continue(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await edit_msg(callback.message.chat.id, callback.message.message_id, 'Вы добавили вложения')
    callback.message.from_user.id = callback.message.chat.id
    callback.message.text = user_data.get('text')
    await load_text(callback.message, state)


@dp.callback_query_handler(text='send_msg', state=FSMNew_question.send)
async def sent_message(callback: types.CallbackQuery, state: FSMContext):
    await edit_msg(callback.message.chat.id, callback.message.message_id, 'Ваш вопрос отправлен!')
    await bd_add_question(callback.message, state)
    await state.finish()
    # TODO разобраться почему иногда отправляются несколько сообщений. Поможет ли решить вопрос sleep
    await asyncio.sleep(3)


# async def caption_text(message, user_data, state: FSMContext):
#     if message.caption:
#         if not user_data.get('text'):
#             async with state.proxy() as data:
#                 data['text'] = message.caption
#             kb = await create_button_reply(2, 'Отмена', 'Назад', text='Отправить')
#             await reply_msg(message, '<b>Отправить вопрос?</b>', kb)
#         else:
#             kb = await create_button_reply(2, 'Отправить', 'Отмена')
#             await reply_msg(message, '<b>Вы уже ввели текст обращения.'
#                                      '\nПодпись к данным файлам учитываться не будет!'
#                                      '\nОтправить вопрос?</b>', kb)


async def load_photo(message: types.Message, state: FSMContext):
    photos = list()
    user_data = await state.get_data()
    value = user_data.get('photos')
    if value:
        for ret in value:
            photos.append(ret)
    photos.append(f'{message.photo[0].file_id}|{message.caption}')
    async with state.proxy() as data:
        data['photos'] = photos
    # await caption_text(message, user_data, state)
    # print(photos)
    # print(message.photo.pop())


async def load_document(message: types.Message, state: FSMContext):
    document = list()
    user_data = await state.get_data()
    value = user_data.get('documents')
    if value:
        for ret in value:
            document.append(ret)
    document.append(f'{message.document.file_id}|{message.caption}')
    async with state.proxy() as data:
        data['documents'] = document
    # await caption_text(message, user_data, state)
    # print(document)


async def load_video(message: types.Message, state: FSMContext):
    video = list()
    user_data = await state.get_data()
    value = user_data.get('videos')
    if value:
        for ret in value:
            video.append(ret)
    video.append(f'{message.video.file_id}|{message.caption}')
    async with state.proxy() as data:
        data['videos'] = video
    # await caption_text(message, user_data, state)
    # print(video)


@dp.callback_query_handler(text='cancel', state='*')
async def cm_cancel(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await edit_msg(callback.message.chat.id, callback.message.message_id, f'Вопрос отменен!')
    await state.finish()


@dp.callback_query_handler(Text(startswith='ok:'))
async def call_ok(callback: types.CallbackQuery):
    question_id = int(callback.data.split(':')[1])
    user_id = int(callback.data.split(':')[2])
    temp = await find_column('delete_msg', 'question_id', question_id)
    msg = temp[0][1].split('|')
    user_name = await get_user_name(callback.message, id_user=callback.message.chat.id)
    logger.info(f'{await get_date_time()} - {user_name} принял заявку №{question_id}')
    for data in msg:
        res = data.split(',')
        if callback.message.chat.id != int(res[0]):
            text = f'{user_name} принял заявку №{question_id}'
            await edit_msg(res[0], res[1], text)
        else:
            kb = create_button_inline(2, t1='Ответить на вопрос', с2=f'work:{question_id}:{user_id}:{res[1]}')
            # kb = create_button_inline(2, t1='Отработал', с2=f'work:{question_id}:{user_id}:{res[1]}',
            #                           t2='Отказать', c2=f'rej:{question_id}:{user_id}:{res[1]}')
            text = f'Вы приняли заявку №{question_id}'
            await edit_msg(res[0], res[1], text, kb)
    await set_bd_update('questions', 'question_id', question_id, 'responsible_id', callback.message.chat.id)
    await set_bd_update('questions', 'question_id', question_id, 'acceptance_time', await get_date_time())
    await callback.answer()
    # await callback.answer(text=f'Вы приняли заявку {str(question_id)}', show_alert=True)
    # await start_response_message()


def registration_handlers_ask_question(_dp: Dispatcher):
    # dp.register_message_handler(cm_new_question,
    #                             chat_type=types.ChatType.PRIVATE, state=None)
    # _dp.register_message_handler(back_fsm, Text(equals='назад', ignore_case=True),
    #                              chat_type=types.ChatType.PRIVATE, state="*")
    # _dp.register_message_handler(load_direction, chat_type=types.ChatType.PRIVATE,
    #                              state=FSMNew_question.direction)
    # _dp.register_message_handler(load_category, chat_type=types.ChatType.PRIVATE,
    #                              state=FSMNew_question.category)
    _dp.register_message_handler(sent_message, Text(equals='отправить', ignore_case=True),
                                 chat_type=types.ChatType.PRIVATE, state=FSMNew_question.send)
    _dp.register_message_handler(load_text, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.TEXT,
                                 state=FSMNew_question.text)
    _dp.register_message_handler(load_photo, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.PHOTO,
                                 state=FSMNew_question.text)
    _dp.register_message_handler(load_photo, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.PHOTO,
                                 state=FSMNew_question.media)
    _dp.register_message_handler(load_document, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.DOCUMENT,
                                 state=FSMNew_question.text)
    _dp.register_message_handler(load_document, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.DOCUMENT,
                                 state=FSMNew_question.media)
    _dp.register_message_handler(load_video, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.VIDEO,
                                 state=FSMNew_question.text)
    _dp.register_message_handler(load_video, chat_type=types.ChatType.PRIVATE,
                                 content_types=types.ContentType.VIDEO,
                                 state=FSMNew_question.media)
