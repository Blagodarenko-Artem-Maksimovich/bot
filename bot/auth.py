from telebot.types import Message

import bot.bot_states
import config
from eduapp.main import login


def auth_enter_login_handler(message: Message, tele_bot, status):
    text = message.text
    if text == 'Назад':
        bot.bot_states.MainState(message, tele_bot, status)
        return
    temporary_login = text
    tele_bot.reply_to(message, f'Вы ввели логин {text}')
    tele_bot.send_message(message.chat.id, 'Введите пароль')
    tele_bot.register_next_step_handler(
        message, auth_enter_password_handler, tele_bot, status, temporary_login)


def auth_enter_password_handler(message: Message, tele_bot, status, temporary_login):
    if message.text == 'Назад':
        bot.bot_states.MainState(message, tele_bot, status)
        return
    text = message.text
    tele_bot.reply_to(message, f'Вы ввели пароль {text}')
    login_data = login(temporary_login, text)

    if login_data.success:
        tele_bot.reply_to(message, 'Авторизация прошла успешно')
        config.USER_LOGIN = temporary_login
        config.USER_PASSWORD = text
    else:
        tele_bot.send_message(message.chat.id, 'Ошибка входа')
        tele_bot.send_message(message.chat.id, login_data.error)

    bot.bot_states.MainState(message, tele_bot, status)
