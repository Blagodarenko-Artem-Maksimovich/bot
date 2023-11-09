"""
UI - пользовательский интерфейс
"""
from typing import Any, Dict

from jinja2 import Environment, PackageLoader, select_autoescape

from constants import MonthNames, LessonStatusSymbols

from eduapp.main import EaAuthStatus


def get_template_to_html(name):
    env = Environment(
        loader=PackageLoader('ui'),
        autoescape=select_autoescape()
    )
    return env.get_template(name)


def login_ui_handler(data: EaAuthStatus) -> str:
    """
    Вывод подтверждение входа или ошибки

    :param data: статус авторизации (успешная или нет)
    :type data: :class:`eduapp.main.EaAuthStatus`
    :return: подтверждение входа
    :rtype: :class:`str`
    """
    return f'Пользователь "{data.username}" успешно залогинился' \
        if data.success else f'Ошибка входа. \n{data.error}'


def profile_data_to_str(data):
    template = get_template_to_html('profile.html')
    context = data
    return template.render(context)


def calendar_data_to_str(data: Dict[str, Any]) -> str:
    """
    Преобразует данные о календаре в строку, которая отправится пользователю

    :param data: изначальные данные о календаре
    :type data: :class:`dict`
    :return: строка с календарём, выводимая пользователю
    :rtype: :class:`str`
    """
    template = get_template_to_html('calendar.html')
    context = {
        'month_name': MonthNames.translate(data['date']['name']),
        'days': []
    }
    for days, lessons in data['days'].items():
        day_context = {
            'date': days,
            'lessons': []
        }
        for lesson in lessons:
            lesson_context = {
                'start': lesson['time']['start'],
                'finish': lesson['time']['finish'],
                'visited': LessonStatusSymbols.translate(lesson['visited']),
                'subject': lesson['name'],
            }
            if 'theme' in lesson:
                lesson_context['theme'] = lesson['theme']
            day_context['lessons'].append(lesson_context)
        context['days'].append(day_context)
    return template.render(context)
