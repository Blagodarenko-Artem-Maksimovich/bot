import logging

from telebot.types import Message

from bot.system import tele_bot


@tele_bot.message_handler(commands=['menu'])
def menu_command_handler(message: Message):
    logging.info('От пользователя `%s` пришла команда `/menu`', message.from_user.username)
    tele_bot.send_message(message.chat.id, 'Привет')
