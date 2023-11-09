import os

import telebot
from dotenv import load_dotenv
from telebot.types import Message

import config
from bot.bot_states import BotStatus
from bot.handlers import StartCommandHandler
from eduapp.main import login

load_dotenv()

token = os.environ.get('TELEGRAM_BOT_TOKEN', 'DEFINE ME!')
tele_bot = telebot.TeleBot(token, parse_mode=None)

bot_status = BotStatus()


@tele_bot.message_handler(commands=['start'])
def start_command_handler(message: Message):
    StartCommandHandler(message, tele_bot, bot_status)
