from settings import bot, token, db, cursor
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, PicklePersistence, CallbackContext
from telegram import Update
from telegram.ext import ContextTypes, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from db import check_user_data, check_video_history
from classes import VLoader
import datetime
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning
import os
from keyboards import main as kb_main


filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)
application = ApplicationBuilder().token(token).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    '''Стартовое приветствующее сообщение'''
    try:
        cursor.execute(f'''DELETE FROM temp_rutube WHERE user_id={update.message.from_user.id};''')
        db.commit()
        mes_text = f'''Приветствую, {update.message.from_user.username}'''
        check_user_data(update)
        buttons = [[InlineKeyboardButton(text="Скачать с рутуба", callback_data="startfromrutube")],[InlineKeyboardButton(text="Мой создатель и Бог", url="https://t.me/itendy")]]
        vid_data_exist = check_video_history(update)
        if vid_data_exist is not None:
            buttons.append([InlineKeyboardButton(text='История', callback_data="showvideohistory")])
        kb = InlineKeyboardMarkup(buttons)
        await bot.delete_message(update.message.from_user.id, update.message.id)
        await bot.send_message(update.message.from_user.id, text=mes_text, reply_markup=kb)
    except:
        cursor.execute(f'''DELETE FROM temp_rutube WHERE user_id={update.callback_query.from_user.id};''')
        db.commit()
        mes_text = f'''Приветствую, {update.callback_query.from_user.first_name} {update.callback_query.from_user.last_name}'''
        check_user_data(update)
        buttons = [[InlineKeyboardButton(text="Скачать с рутуба", callback_data="startfromrutube")],[InlineKeyboardButton(text="Мой создатель и Бог", url="https://t.me/itendy")]]
        vid_data_exist = check_video_history(update)
        if vid_data_exist is not None:
            buttons.append([InlineKeyboardButton(text='История', callback_data="showvideohistory")])
        kb = InlineKeyboardMarkup(buttons)
        await bot.send_message(update.callback_query.from_user.id, text=mes_text, reply_markup=kb)



async def link1(update: Update, context: CallbackContext) -> int:
    '''Вспомогательная функция для ввода пользователем ссылки на видео в Рутубе'''
    await bot.send_message(chat_id=update.callback_query.from_user.id, text="Введите ссылку на видео в Rutube")
    return 1


async def link2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''Выдает пользователю в чате всю информацию о найденном в рутубе видео и доступных для скачивания разрешениях'''
    cursor.execute(f'''INSERT INTO temp_rutube (user_id, link) VALUES({update.message.from_user.id}, "{update.message.text}");''')
    db.commit()
    video_data = VLoader(update.message.text).check_video_info()
    text = f'''Мы нашли следующее видео:

Название: {video_data[1]}
Описание: 
{video_data[2]}...
Длительность: {str(datetime.timedelta(seconds=video_data[3] // 1000))}'''
    await bot.send_photo(chat_id=update.message.from_user.id, photo=video_data[0], caption=text, reply_markup=InlineKeyboardMarkup(video_data[5]))
    return 2

async def rutube_dload(update: Update, context: CallbackContext) -> int:
    cursor.execute(f'''SELECT link FROM temp_rutube WHERE user_id={update.callback_query.from_user.id}''')
    link = cursor.fetchone()[0]
    await bot.send_message(chat_id=update.callback_query.from_user.id, text="Ваше видео уже скачивается, подождите")
    final_file = VLoader(link).download(update.callback_query.data.split("_")[-1], filename=f"{update.callback_query.from_user.id}")    
    await bot.send_video(chat_id=update.callback_query.from_user.id, video=f"./downloads/rutube/{update.callback_query.from_user.id}.mp4", caption="Вот ваше видео!", reply_markup=kb_main.gotostart)
    data = VLoader(link).check_video_info()
    cursor.execute(f'''INSERT INTO history (user_id, title, link, desc, duration, source) VALUES({update.callback_query.from_user.id}, "{data[1]}", "{link}", "{data[2]}", "{data[3]}", "rutube")''')
    db.commit()
    cursor.execute(f'''DELETE FROM temp_rutube WHERE user_id={update.callback_query.from_user.id};''')
    db.commit()
    os.remove(f"./downloads/rutube/{update.callback_query.from_user.id}.mp4")
    return -1


async def fallback_rutube(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return -1    
        

def reg_main_handlers():
    application.add_handler(CommandHandler("start", start))
    application.add_handler(ConversationHandler(entry_points=[CallbackQueryHandler(callback=link1, pattern=(lambda callback_data: callback_data == "startfromrutube"))], 
                                                states={
                                                    1: [MessageHandler(callback=link2, filters=filters.TEXT)],
                                                    2: [CallbackQueryHandler(callback=rutube_dload, pattern=(lambda callback_data: "get_res_" in callback_data))]
                                                }, fallbacks=[CallbackQueryHandler(callback=start, pattern=(lambda callback_data: callback_data == "gotostartmenu"))]))
    application.add_handler(CallbackQueryHandler(callback=start, pattern=(lambda callback_data: callback_data == "gotostartmenu")))
    
