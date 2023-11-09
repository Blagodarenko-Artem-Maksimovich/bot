""" Файл с хэндлерами бота """

import logging
from abc import ABC

import telebot

import bot.bot_states
import bot.main
import config
from bot.auth import auth_enter_login_handler
from bot.calendar import input_date_period
from bot.questions import parse_question_number
from eduapp.main import login, get_calendar_data, get_profile_data
from eduapp.urls import EAUrls
from ui.main import calendar_data_to_str, profile_data_to_str


class BotStructure(ABC):
    """
    Базовый абстрактный класс любой структуры бота,
    От него должны наследоваться все другие состояния, хэндлеры и все остальное
    """

    def __init__(self, message):
        """
        Базовый конструктор структуры бота: пишет в лог информацию о команде,
        которая пришла боту от пользователя.

        :param message: сообщение пользователя
        :type message: telebot.types.Message
        """
        logging.info('От пользователя `%s` пришла команда `%s`', message.from_user.username, message.text)


class HandlerStructure(BotStructure):
    """
    Базовый класс хэндлера бота,
    От него должны наследоваться все другие хэндлеры
    """

    def __init__(self, message, t_bot, status_of_bot, back_to_state):
        """
        Базовый конструктор хэндлера бота:

        1. Вызывает конструктор структуры бота
        2. Переключает состояние бота на то, которое должно включиться после
           выполнения хэндлера

        :param message: сообщение пользователя
        :type message: telebot.types.Message
        :param t_bot: сам бот
        :type t_bot: telebot.TeleBot
        :param status_of_bot: класс, отслеживающий состояние бота
        :type status_of_bot: BotStatus
        :param back_to_state: состояние, которое должно включиться после выполнения хэндлера
        :type back_to_state: bot.bot_states.BotState
        """

        super().__init__(message)
        status_of_bot.state = back_to_state(message, t_bot, status_of_bot)


class StartCommandHandler(HandlerStructure):
    """
    Хэндлер стартовой команды (главного меню).
    """

    def __init__(self, message, t_bot, status_of_bot):
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.GuestState)


class HelpCommandHandler(HandlerStructure):
    """
    Хэндлер команды "Что умеет этот бот?"
    """

    def __init__(self, message, t_bot, status_of_bot):
        t_bot.reply_to(message, "Этот бот разработан для более удобного взаимодействия учеников с сервисами ШП."
                                "\n\nС помощью него вы можете за пару кликов: "
                                "\n\n ⦿ Узнать расписание занятий "
                                "\n\n ⦿ Просмотреть свой профиль "
                                "\n\n ⦿ Задать вопрос преподавателю"
                                "\n\n И многое другое")
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.MainState)


class LoginCommandHandler(HandlerStructure):
    """
    Хэндлер команды авторизации.
    """

    def __init__(self, message, t_bot, status_of_bot):
        logging.info('От пользователя `%s` пришла команда авторизации', message.from_user.username)
        t_bot.send_message(message.chat.id, 'Введите "В меню" если захотите вернуться на главное меню')
        t_bot.send_message(message.chat.id, 'Введите логин')
        t_bot.register_next_step_handler(message, auth_enter_login_handler, t_bot, status_of_bot)


class ProfileCommandHandler(HandlerStructure):
    """
    Хэндлер команды получения данных о пользователе
    """

    def __init__(self, message, t_bot, status_of_bot):
        jsn = get_profile_data()
        text = profile_data_to_str(jsn)
        t_bot.send_message(message.chat.id, text, parse_mode='HTML')
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.MainState)


class CalendarMenuCommandHandler(HandlerStructure):
    """
    Хэндлер команды меню календаря.
    """

    def __init__(self, message, t_bot, status_of_bot):
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.CalendarState)


class CalendarCommandHandler(HandlerStructure):
    """
    Хэндлер команды получения расписания.
    """

    def __init__(self, message, t_bot, status_of_bot, start_date=None, end_date=None):
        if start_date:
            self.get_calendar(message=message, t_bot=t_bot, start_date=start_date, end_date=end_date)
        else:
            if message.text == "Расписание на предыдущий месяц":
                self.get_calendar(message, t_bot, month=-1)
            elif message.text == "Расписание на следующий месяц":
                self.get_calendar(message, t_bot, month=1)
            else:
                self.get_calendar(message, t_bot)
            super().__init__(message, t_bot, status_of_bot, bot.bot_states.CalendarState)

    @staticmethod
    def get_calendar(message, t_bot, month=0, start_date=None, end_date=None):
        jsn = get_calendar_data(start=start_date, end=end_date, month=month)
        if not jsn['success']:
            login(config.USER_LOGIN, config.USER_PASSWORD)
            jsn = get_calendar_data(start=start_date, end=end_date, month=month)
        if not jsn['success']:
            t_bot.send_message(message.chat.id, 'На этом отрезке времени нет занятий')
            return
        try:
            text = calendar_data_to_str(jsn)
            t_bot.send_message(message.chat.id, text, parse_mode='HTML')
        except TypeError:
            t_bot.send_message(message.chat.id, 'На этом отрезке времени нет занятий')


class CalendarFromPeriodCommandHandler(HandlerStructure):
    """
    Хэндлер команды получения расписания за указанный период.
    """

    def __init__(self, message, t_bot, status_of_bot):
        t_bot.send_message(message.chat.id, 'Пожалуйста, введите период в формате DD.MM-DD.MM')
        t_bot.register_next_step_handler(message, input_date_period, t_bot, status_of_bot)


class QuePageCommandHandler(HandlerStructure):
    """
    Хэндлер перелистывания на следующую/предыдущую страницу с вопросами
    """

    def __init__(self, message, t_bot, status_of_bot):
        if message.text == 'Отобразить следующие пять вопросов':
            bot.bot_states.QuestionsState.page += 1
        else:
            bot.bot_states.QuestionsState.page -= 1
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.QuestionsState)


class OpenQueCommandHandler(HandlerStructure):
    """
    Хэндлер открывания определённого вопроса
    """

    def __init__(self, message, t_bot, status_of_bot):
        t_bot.send_message(message.chat.id, 'Введите номер вопроса, который хотите открыть')
        t_bot.register_next_step_handler(message, parse_question_number, t_bot, status_of_bot)


class AskCommandHandler(HandlerStructure):
    """
    Хэндлер написания вопроса в eduapp
    """

    def __init__(self, message, t_bot, status_of_bot):
        t_bot.send_message(message.chat.id,
                           f'Вы можете написать вопрос по этой ссылке: {config.EDUAPP_BASE_URL + f"/pupil/discussions/{bot.bot_states.QueChatState.discussion}/"}')
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.QuestionsState)


class PreviousPageChat(HandlerStructure):
    """
    Хэндлер открывания предыдущих десяти реплик
    """

    def __init__(self, message, t_bot, status_of_bot):
        bot.bot_states.QueChatState.page += 1
        super().__init__(message, t_bot, status_of_bot, bot.bot_states.QueChatState.page)
