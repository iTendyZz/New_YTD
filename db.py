from settings import db, cursor

def insert_user_data(update):
    '''Вносит данные о пользователе в БД, если их не было'''
    cursor.execute(f'''INSERT INTO users (user_id, username, first_name, last_name) VALUES ({update.message.from_user.id}, "{update.message.from_user.username}", "{update.message.from_user.first_name}", "{update.message.from_user.last_name}");''')
    db.commit()


def update_user_data(update):
    '''Обновляет данные о пользователе в БД при изменениях'''
    try:
        cursor.execute(f'''UPDATE users SET username="{update.message.from_user.username}", first_name="{update.message.from_user.first_name}", last_name="{update.message.from_user.last_name}" WHERE user_id={update.message.from_user.id}''')
        db.commit()
    except:
        cursor.execute(f'''UPDATE users SET username="{update.callback_query.from_user.username}", first_name="{update.callback_query.from_user.first_name}", last_name="{update.callback_query.from_user.last_name}" WHERE user_id={update.callback_query.from_user.id}''')
        db.commit()


def check_user_data(update):
    '''Функция проверки, регистрации и обновления данных о пользователе в БД'''
    try:
        upd = update
        cursor.execute(f'''SELECT * FROM users WHERE user_id={upd.message.from_user.id}''')
        us_data = cursor.fetchone()
        if us_data is None:
            insert_user_data(upd)
        else:
            if (us_data[2] != update.message.from_user.username) or (us_data[3] != update.message.from_user.first_name) or (us_data[4] != update.message.from_user.last_name):
                update_user_data(upd)
    except:
        upd = update
        cursor.execute(f'''SELECT * FROM users WHERE user_id={upd.callback_query.from_user.id}''')
        us_data = cursor.fetchone()
        if us_data is None:
            insert_user_data(upd)
        else:
            if (us_data[2] != update.callback_query.from_user.username) or (us_data[3] != update.callback_query.from_user.first_name) or (us_data[4] != update.callback_query.from_user.last_name):
                update_user_data(upd)


def add_video_to_history(update, video_data):
    '''Добавляет видео в историю скачиваний'''
    pass


def check_video_history(update):
    try:
        cursor.execute(f'''SELECT id FROM history WHERE user_id={update.message.from_user.id}''')
    except:
        cursor.execute(f'''SELECT id FROM history WHERE user_id={update.callback_query.from_user.id}''')
    vid_data_exist = cursor.fetchall()
    if len(vid_data_exist) == 0:
        return None
    else:
        return vid_data_exist