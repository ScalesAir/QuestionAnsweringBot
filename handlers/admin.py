# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import bot
from data_base.sqlite_bd import sql_read, find_column, find_no_end_questions, delete_bd_msg, delete_line_bd_msg
from functions.other_func import get_user_name, get_date_time
from keyboards.client_kb import create_button_inline
from functions.message_func import send_msg, edit_msg
from logs import logging

logger = logging.getLogger("app.handlers.admin")

__all__ = ['registration_handlers_admin',
           'check_ban',
           'check_moderator']


async def check_ban(user_id):
    temp = await sql_read('ban')
    for ret in temp:
        if user_id == ret[0]:
            return True
    return False


async def check_moderator():
    temp = await sql_read('moderator')
    return temp


async def add_ban(message: types.Message):
    print(await check_ban(message.from_user.id))


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


async def create_document_group(documents, caption=''):
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


async def checking_questions(message: types.Message):
    try:
        del_msg = await find_no_end_questions()
        user_id = ''
        question_id=''
        print(del_msg)
        for index in del_msg:
            msg_id = list()
            question_id = index[0]
            questions = await find_column('questions', 'question_id', question_id)
            msg = index[1].split('|')
            print(questions)
            for question in questions:

                user_id = question[1]
                print('user_id', user_id)
                text = question[4]
                edit_text = f"Не отвеченная заявка №{question_id} от " \
                            f"{await get_user_name(message, user_id)}:" \
                            f"\n{text}"
                print(text)
                photo = list().append(question[5])
                video = list().append(question[6])
                document = list().append(question[7])
                print(msg)
                for data in msg:
                    res = data.split(',')
                    responsible_id = res[0]
                    print(responsible_id)
                    print(text)
                    await edit_msg(res[0], res[1], f'Данная заявка повторена {await get_date_time()}')
                    media = None
                    doc = None
                    if photo or video:
                        media = await create_media_group(photo, video)

                    if document:
                        doc = await create_document_group(document)
                    kb = create_button_inline(2, t1='Принять в работу',
                                              c1=f"ok:{question_id}:{user_id}")

                    # if not user_data.get('photos') and not user_data.get('videos') and not user_data.get('documents'):
                    #     text = caption
                    # print(type(id_user), id_user, type(message.from_user.id), message.from_user.id)
                    if responsible_id != str(user_id) or \
                            responsible_id == str(1621516433) or responsible_id == str(541261735):
                        if media:
                            # await types.ChatActions.upload_photo()
                            await bot.send_media_group(responsible_id, media=media)
                        if doc:
                            await bot.send_media_group(responsible_id, media=doc)
                        # if text != '':  # Если есть (фото или видео) и документ, то текст оправить отдельно
                        await send_msg(message, edit_text, spec_chat_id=responsible_id)
                        msg = await send_msg(message, 'Принять заявку?', spec_chat_id=responsible_id, rm=kb)
                        if msg:
                            msg_id.append(str(responsible_id) + ',' + str(msg.message_id))
                        else:
                            logger.warning(f'{await get_user_name(message, responsible_id)} заблокировал пользователя')

                await delete_line_bd_msg(question_id)
                await delete_bd_msg(int(question_id), '|'.join(msg_id))
            logger.info(
                f"{await get_date_time()} - {await get_user_name(message, user_id)} создал заявку №{question_id}")
    except Exception as err:
        logger.error(err)


def registration_handlers_admin(_dp: Dispatcher):
    """Функция регистрации Хендлеров, при этом декораторы не нужны

    :param _dp:
    :return:
    """

    _dp.register_message_handler(checking_questions, commands=['check'], state=None)
    _dp.register_message_handler(add_ban, commands=['ban'], state=None)
