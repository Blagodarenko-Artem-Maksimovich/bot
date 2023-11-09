"""
Хранилище всех URL системы Eduapp, необходимых для работы бота
"""

from config import EDUAPP_API_URL


class EAUrls:
    """
    Набор URLов, используемых в ЕА для работы по API
    """

    #: URL авторизации на сервере LMS Eduapp
    LOGIN_URL: str = EDUAPP_API_URL + '/rest-auth/login/'

    #: URL для получения базовой информации о залогиненном пользователе
    ACCOUNT_URL: str = EDUAPP_API_URL + '/account/'

    #: URL для получения информации о календаре пользователя
    CALENDAR_DATA_URL_PATTERN = EDUAPP_API_URL + '/teaching_situation/classes_users/extended/'

    #: GET-параметры запроса получения информации о календаре пользователя
    CALENDAR_DATA_URL_PARAMS = {
        'classes__datetime_begin__gte': 'DEFINE_ME!',
        'classes__datetime_begin__lte': 'DEFINE_ME!',
        'user_id': '{id}',
        'orderBy': 'classes__datetime_begin',
        'classes__course__usage__in': 'M,D,B,S',
        'page': '1',
        'limit': '100'
    }

    #: URL для получения информации об обсуждениях пользователя
    QUESTION_URL = EDUAPP_API_URL + '/discussions/'

    @staticmethod
    def get_calendar_data_url(start, end, user_id):
        url = EAUrls.CALENDAR_DATA_URL_PATTERN
        params = EAUrls.CALENDAR_DATA_URL_PARAMS
        params['classes__datetime_begin__gte'] = str(start.date())
        params['classes__datetime_begin__lte'] = str(end.date())
        params['user_id'] = user_id
        params_list = [f'{key}={value}' for key, value in params.items()]
        params_url = '&'.join(params_list)
        return f'{url}?{params_url}'

    @staticmethod
    def get_chat_comments_url(discussion):
        return EAUrls.QUESTION_URL + str(discussion) + '/comments/'
