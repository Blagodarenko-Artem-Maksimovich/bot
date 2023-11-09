"""
Основной модуль для работы с API Eduapp
"""

import dataclasses
import logging
from datetime import datetime
from typing import Optional, Tuple

import requests
from dateutil.relativedelta import relativedelta
from requests import Response

import config
from eduapp.exceptions import CaptchaEnabledError, InvalidPasswordError, UnknownError
from eduapp.urls import EAUrls


class InvalidPassword(RuntimeError):
    pass


class Authenticator:
    """
    Аутентификационный класс.

    Позволяет при помощи функции login() - авторизоваться на площадке EduApp
    """

    # pylint: disable=E1101,W0105:
    # Добавлено, чтобы не ругался на модуль requests

    """Коды ошибки в HTTP-запросах"""
    BAD_STATUS_CODES = [
        requests.codes.bad_request,
        requests.codes.forbidden,
        requests.codes.unauthorized
    ]

    def __init__(self, username: str = 'define me!',
                 password: str = 'define me!', token: str = None) -> None:
        """
        Просто конструктор. Просто инициализирует поля

        :param username: имя пользователя
        :param password: пароль пользователя
        :param token: токен jwt-авторизации. Может отсутствовать
        """
        self.username: str = username
        self.password: str = password
        self.token: str = token
        self.user: Optional[str] = None

    def login(self) -> Tuple[str, str]:
        """
        Основная функция для авторизации. Логинится в едуапп или падает с исключениями

        :raise CaptchaEnabledError: в случае, если данный IP-адрес покажется системе подозрительным
        :raise InvalidPasswordError: в случае, если данные для входа указаны некорректно
        :raise UnknownError: если ошибка есть, но не получилось определить, какая.
        :return: Пара из имени/фамилии и токена
        """
        response = self.__get_login_response()
        self.__parse_status_code(response)
        self.__request_user_data()
        return self.user, self.token

    def __get_login_response(self) -> Response:
        """
        Отправка запроса на авторизацию и возвращение ответа

        :return: ответ на запрос авторизации
        """
        logging.debug('Отправляем запрос на авторизацию. URL: %s', EAUrls.LOGIN_URL)
        response = requests.post(
            EAUrls.LOGIN_URL,
            data={'username': self.username, 'password': self.password, 'add_captcha': False}
        )
        return response

    def __parse_status_code(self, response: Response) -> None:
        """
        Обрабатываем код ответа сервера и кидаем исключения, если что-то идёт не так
        :param response: ответ от сервера
        :raise CaptchaEnabledError: в случае, если данный IP-адрес покажется системе подозрительным
        :raise InvalidPasswordError: в случае, если данные для входа указаны некорректно
        :raise UnknownError: если ошибка есть, но не получилось определить, какая.
        """
        if response.status_code == requests.codes.ok:
            logging.info('Авторизация успешна')
            self.token = response.json()['token']
            config.EDUAPP_JWT = self.token
            return
        if response.status_code == requests.codes.bad_request:
            logging.info('Ошибка авторизации. Status code: %i', response.status_code)
            self.token = None
            if 'captcha' in response.json().keys():
                raise CaptchaEnabledError()
            if 'non_field_errors' in response.json().keys():
                raise InvalidPasswordError()
            return
        logging.info('Какая-то непонятная ошибка. Status code: %i', response.status_code)
        raise UnknownError()

    def __request_user_data(self) -> None:
        """
        Запрашиваем данные пользователя. Если получилось - сохраняем их, иначе - кидаем исключение
        return True

        :raise InvalidPasswordError: в случае, если данные для входа указаны некорректно
        """
        logging.debug('Пробуем получить данные пользователя')
        self.user = self.__get_account_data()
        if not self.user:
            logging.info('Ошибка авторизации')
            raise InvalidPasswordError()

    def __get_account_data(self) -> Optional[str]:
        """
        Отправка запроса на получение данных аккаунта и возвращение ответа

        :return: Имя и фамилия, если авторизация успешна и None в случае неуспешной авторизации
        """
        logging.debug('Отправляем запрос на получение даных пользователя. URL: %s',
                      EAUrls.ACCOUNT_URL)
        response = requests.get(
            EAUrls.ACCOUNT_URL,
            cookies={
                'eduapp_jwt': self.token
            },
            headers={
                'host': 'my.informatics.ru',
                'referer': 'https://my.informatics.ru/pupil/root/'
            }
        )
        if response.status_code in Authenticator.BAD_STATUS_CODES:
            logging.info('Ошибка авторизации. Status_code: %i', response.status_code)
            return None
        return f"{response.json()['last_name']} {response.json()['first_name']}"


@dataclasses.dataclass
class EaAuthStatus:
    """
    Статус ответа от аутентификатора, инкапсулирующий в себе
    либо данные для доступа, либо данные об ошибке
    """

    #: Статус операции. Допустимые значения: `True` и `False`
    success: bool

    #: Имя пользователя, строка.
    username: Optional[str] = None

    #: Токен пользователя, строка.
    token: Optional[str] = None

    #: Сообщение об ошибке. Заполняется только в том случае,
    #: если поле `success` приняло значение `False`
    error: str = ''


def login(username: str, password: str) -> EaAuthStatus:
    """
    Основная функция для авторизации. Логинится в едуапп и выдаёт статус в качестве результата

    :param username: Имя пользователя
    :param password: Пароль пользователя
    :return: Пара из имени/фамилии и токена (или детали ошибки)
    """
    logging.debug('Trying to access to eduapp')
    auth = Authenticator(username, password, None)
    try:
        username, token = auth.login()
    except (InvalidPasswordError, CaptchaEnabledError, UnknownError) as ex:
        return EaAuthStatus(success=False, error=str(ex))
    return EaAuthStatus(success=True, username=username, token=token)


def get_profile_data():
    response = requests.get(EAUrls.ACCOUNT_URL, cookies={'eduapp_jwt': config.EDUAPP_JWT})
    jsn = response.json()
    return {'first_name': jsn['first_name'],
            'last_name': jsn['last_name'],
            'patronymic': jsn['patronymic'],
            'phone': jsn['contact_number'],
            'email': jsn['email'],
            'timezone': jsn['timezone']
            }


def get_calendar_data_from_website(cookies, start, end):
    """
    Эта функция получает данные о календаре с eduapp

    :param cookies: нужные куки
    :param start: получение данных о календаре с этой даты
    :param end: получение данных о календаре до этой даты
    :return: словарь с данными
    """
    user_id = str(requests.get(EAUrls.ACCOUNT_URL, cookies=cookies).json()['id'])
    return requests.get(EAUrls.get_calendar_data_url(start, end, user_id), cookies=cookies)


def calendar_data_to_good_json(response):
    """
    Преобразует данные о календаре, полученные с сайта в удобный для использования словарь

    :param response: ответ с сайта
    :return: красивый словарь
    """
    if not response.json()['results']:
        return {'success': False}

    res_json = get_meta_data(response)

    for lesson in response.json()['results']:
        res = get_main_data_of_lesson(lesson)

        get_data_about_visit(lesson, res)

        classes_date = datetime.strptime(lesson['classes']['date_of'], "%Y-%m-%d")
        classes_date_str = classes_date.strftime("%d.%m")

        if classes_date_str in res_json['days']:
            res_json['days'][classes_date_str].append(res)
        else:
            res_json['days'][classes_date_str] = [res]
    res_json['success'] = True
    return res_json


def get_datetime_from_ea_string(data):
    data_without_timezone = data[:-6]
    ea_datetime_format = "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(data_without_timezone, ea_datetime_format)


def get_main_data_of_lesson(lesson):
    start_time = get_datetime_from_ea_string(lesson['classes']['datetime_begin'])
    finish_time = get_datetime_from_ea_string(lesson['classes']['datetime_end'])
    res = {
        'name': lesson['classes']['course']['simplest_name'],
        'time': {
            'start': start_time,
            'finish': finish_time,
        },
        'base': lesson['classes']['course']['diary_type'] == 'D',
    }
    if len(lesson['classes']['classes_lessons']) > 0:
        res['theme'] = lesson['classes']['classes_lessons'][0]['lesson']['name']
    return res


def get_data_about_visit(lesson, res):
    try:
        if not lesson['pupil_attendances'][0]['is_begun']:
            res['visited'] = 'Предстоит'
        elif lesson['pupil_attendances'][0]['status'] == 'н':
            res['visited'] = 'Пропущено'
        else:
            res['visited'] = 'Посещено'
    except IndexError:
        res['visited'] = 'Предстоит'


def get_meta_data(response):
    res_json = {
        'date': {
            'year': int(response.json()['results'][0]['classes']['date_of'].split('-')[0]),
            'name': datetime(1, int(response.json()['results'][0]['classes']['date_of'].split('-')[1]),
                             1).strftime('%B').lower()
        },
        'days': {}
    }
    return res_json


def get_calendar_data(start=None, end=None, month=0):
    """
    Получает данные с сайта преобразует в красивый словарь

    :param start: получение данных о календаре с этой даты
    :param end: получение данных о календаре до этой даты
    :param month: либо -1, либо 1. Соответственно предыдущий или следующий месяц. Если 0, то берём текущий месяц
    :return: красивый словарь с данными о календаре
    """
    if not start and not end:
        start = datetime.now().astimezone().replace(day=1)
        end = datetime.now().astimezone().replace(day=1) + relativedelta(months=1)

    start += relativedelta(months=month)
    end += relativedelta(months=month)

    response = get_calendar_data_from_website({'eduapp_jwt': config.EDUAPP_JWT}, start, end)

    return calendar_data_to_good_json(response)
