""" Файл с состояниями бота """

import logging
import types

from telebot.types import KeyboardButton, ReplyKeyboardMarkup

import bot.main
from bot.auth import auth_enter_login_handler
from bot.handlers import BotStructure, PreviousPageChat, QuePageCommandHandler, \
    OpenQueCommandHandler, AskCommandHandler
from eduapp.questions import get_question_page_json, open_question
from ui.questions import question_page_to_str, single_question_to_str


class BotState(BotStructure):
    """
    Базовый абстрактный класс состояния бота,
    От него должны наследоваться все другие состояния
    """

    buttons = []
    text = 'Define me!'
    next = {}

    def __init__(self, message, t_bot, status_of_bot):
        """
        Базовый конструктор состояния бота:

        1. Создает меню, состоящее из кнопок (self.buttons - массив строчек с названием кнопок),
        2. Выводит сообщение меню (self.text - строка)
        3. Переключение обработчика на функцию processing (self.processing - функция)

        :param message: сообщение пользователя
        :type message: telebot.types.Message
        :param t_bot: собственно, сам бот
        :type t_bot: telebot.TeleBot
        :param status_of_bot: класс, отслеживающий состояние бота
        :type status_of_bot: BotStatus
        """
        self.menu = SubMenu(self.buttons, self.text, message, t_bot, self.processing, status_of_bot)

    def processing(self, message, t_bot, status_of_bot):
        """
        Метод-обработчик, который определяет, куда нужно переключиться после
        следующего сообщения от пользователя.

        Он сравнивает ключи в словаре next с сообщением от пользователя и,
        в зависимости от результата сравнения, вызывает нужную функцию
        или переходит в другое состояние

        :param message: сообщение пользователя
        :type message: telebot.types.Message
        :param t_bot: сам бот
        :type t_bot: telebot.TeleBot
        :param status_of_bot: класс, отслеживающий состояние бота
        :type status_of_bot: BotStatus
        """
        if message.text in self.next.keys():
            self.next[message.text](message, t_bot, status_of_bot)
        else:
            logging.info('От пользователя `%s` пришло: `{message.text}`',
                         message.from_user.username)
            t_bot.send_message(message.chat.id, "Команда не распознана")
            self.__init__(message, t_bot, status_of_bot)


class GuestState(BotState):
    """
    Состояние неавторизованного пользователя
    """

    def __init__(self, message, t_bot, status_of_bot):
        self.text = 'Вы находитесь в гостевом меню...\nАвторизуйтесь чтобы получить доступ к функциям бота'
        self.buttons = ['Авторизация']
        self.next = {
            'Авторизация': AuthState,
        }
        super().__init__(message, t_bot, status_of_bot)


class MainState(BotState):
    """
    Состояние главного меню.
    """

    def __init__(self, message, t_bot, status_of_bot):
        self.text = 'Вы находитесь в главном меню...'
        self.buttons = ['Календарь', 'Вопросы', 'Профиль', 'Авторизация', 'Что умеет этот бот?']
        self.next = {
            'Календарь': CalendarState,
            'Вопросы': QuestionsState,
            'Профиль': bot.handlers.ProfileCommandHandler,
            'Авторизация': AuthState,
            'Что умеет этот бот?': bot.handlers.HelpCommandHandler,
        }
        super().__init__(message, t_bot, status_of_bot)


class CalendarState(BotState):
    """
    Состояние меню календаря.
    """

    def __init__(self, message, t_bot, status_of_bot):
        self.text = 'Вы находитесь в меню календаря...'
        self.buttons = ['Расписание на текущий месяц', 'Расписание по указанному периоду',
                        'Расписание на предыдущий месяц', 'Расписание на следующий месяц', 'Назад']
        self.next = {
            'Расписание на текущий месяц': bot.handlers.CalendarCommandHandler,
            'Расписание по указанному периоду': bot.handlers.CalendarFromPeriodCommandHandler,
            'Расписание на предыдущий месяц': bot.handlers.CalendarCommandHandler,
            'Расписание на следующий месяц': bot.handlers.CalendarCommandHandler,
            'Назад': MainState
        }
        super().__init__(message, t_bot, status_of_bot)


class AuthState(BotState):
    """
    Состояние меню авторизации.
    """

    def __init__(self, message, t_bot, status_of_bot):
        self.text = 'Вы перешли в меню авторизации...\n\n' \
                    'Введите логин:'
        self.buttons = ['Назад']
        self.next = {
            'Назад': MainState,
        }
        self.menu = SubMenu(self.buttons, self.text, message, t_bot,
                            auth_enter_login_handler, status_of_bot)


class QuestionsState(BotState):
    """
    Состояние меню вопросов.
    """
    page = 1

    def __init__(self, message, t_bot, status_of_bot):
        response = get_question_page_json(QuestionsState.page)
        if response.error:
            t_bot.send_message(message.chat.id, response.error)
            QuestionsState.page -= 1
            super().__init__(message, t_bot, status_of_bot)
            return

        text = question_page_to_str(response.data)
        self.text = text
        self.buttons = ['Открыть вопрос', 'Назад']
        self.next = {
            'Открыть вопрос': OpenQueCommandHandler,
            'Назад': MainState
        }
        if response.data['real_count'] > 5:
            self.buttons.insert(1, 'Отобразить следующие пять вопросов')
            self.next['Отобразить следующие пять вопросов'] = QuePageCommandHandler
        if QuestionsState.page >= 2:
            self.buttons.insert(2, 'Отобразить предыдущие пять вопросов')
            self.next['Отобразить предыдущие пять вопросов'] = QuePageCommandHandler
        super().__init__(message, t_bot, status_of_bot)


class QueChatState(BotState):
    """
    Состояние меню определённого вопроса.
    """
    discussion = 0
    page = 1

    def __init__(self, message, t_bot, status_of_bot):
        jsn, phrases = open_question(message)
        QueChatState.discussion = jsn['id']
        stroka = single_question_to_str(jsn, phrases)
        self.text = stroka
        self.buttons = ['Написать сообщение', 'Назад']
        self.next = {
            'Написать сообщение': AskCommandHandler,
            'Назад': QuestionsState
        }
        if len(phrases) > 10:
            self.buttons.insert(1, 'Отобразить предыдущие 10 сообщений')
            self.next['Отобразить предыдущие 10 сообщений'] = PreviousPageChat
        super().__init__(message, t_bot, status_of_bot)


class SubMenu:
    """
    Класс меню с базовым UI интерфейсом в виде
    набора кнопок.
    """

    def __init__(self, buttons, text, message, t_bot, func, status_of_bot):
        """
        Конструктор меню

        :param buttons: массив строчек с названиями кнопок
        :type buttons: list(str)
        :param text: сообщение, которое выводится при переходе в меню
        :type text: str
        :param message: сообщение пользователя
        :type message: telebot.types.Message
        :param t_bot: сам бот
        :type t_bot: telebot.TeleBot
        :param func: функция-обработчик следующего сообщения пользователя
        :type func: types.FunctionType
        :param status_of_bot: класс, отслеживающий состояние бота
        :type status_of_bot: BotStatus
        """
        self.buttons = []
        for item in buttons:
            self.buttons.append(KeyboardButton(text=item))

        self.keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

        for item in self.buttons:
            self.keyboard.add(item)

        t_bot.send_message(message.chat.id, text, reply_markup=self.keyboard, parse_mode='HTML')
        t_bot.register_next_step_handler(message, func, t_bot, status_of_bot)


class BotStatus:
    state: BotState
