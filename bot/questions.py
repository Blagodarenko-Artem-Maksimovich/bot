import requests
from telebot.types import Message

import config
import bot.bot_states
from eduapp.questions import get_question_page_json
from eduapp.urls import EAUrls


def parse_question_number(message: Message, t_bot, status):
    if message.text == 'Назад':
        bot.bot_states.QuestionsState(message, t_bot, status)
        return
    first_num = bot.bot_states.QuestionsState.page * 5
    try:
        if 1 <= int(message.text) <= first_num:
            bot.bot_states.QueChatState(message, t_bot, status)
        else:
            t_bot.send_message(message.chat.id, f'Введите число от 1 до {first_num} или "Назад" если хотите выйти')
            t_bot.register_next_step_handler(message, parse_question_number, t_bot, status)
    except ValueError:
        t_bot.send_message(message.chat.id, f'Введите число от 1 до {first_num} или "Назад" если хотите выйти')
        t_bot.register_next_step_handler(message, parse_question_number, t_bot, status)
