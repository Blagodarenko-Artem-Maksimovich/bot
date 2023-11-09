from dataclasses import dataclass
from datetime import datetime
from typing import List

import requests

import bot.bot_states
import config
from eduapp.main import get_datetime_from_ea_string
from eduapp.urls import EAUrls


@dataclass
class EaQuestionResponseStatus:
    """
    Статус ответа от функции получения списка вопросов, инкапсулирующий в себе
    либо данные для отображения, либо данные об ошибке
    """

    #: Статус операции. Допустимые значения: `True` и `False`
    success: bool

    #: Данные о вопросах, пришедшие из ЕА
    data: dict

    #: Сообщение об ошибке. Заполняется только в том случае,
    #: если поле `success` приняло значение `False`
    error: str = ''


def get_concrete_questions_page(questions_data: List[dict], page_number: int) -> List[dict]:
    start_question_index = (page_number - 1) * 5
    finish_question_index = page_number * 5
    if start_question_index >= len(questions_data):
        raise RuntimeError('Некорректный номер страницы')
    return questions_data[start_question_index: finish_question_index]


def get_teacher(question) -> str:
    non_pupil_users = list(filter(lambda x: not x['is_client'], question['discussion_users']))
    if len(non_pupil_users) == 0:
        return 'Без отвечающего преподавателя'
    teacher = non_pupil_users[0].get('user', None)
    if not teacher:
        raise RuntimeError('В объекте преподавателя отсутствует секция user')
    first_name = teacher.get('first_name', 'DEFAULT_TEACHER_FIRST_NAME')
    last_name = teacher.get('last_name', 'DEFAULT_TEACHER_LAST_NAME')
    return f'{first_name} {last_name}'


def get_question_page_json(page=1) -> EaQuestionResponseStatus:
    cookies = {'eduapp_jwt': config.EDUAPP_JWT}
    response = requests.get(EAUrls.QUESTION_URL, cookies=cookies)
    if response.status_code != requests.codes.ok:
        return EaQuestionResponseStatus(False, {}, 'Пришёл некорректный ответ от сервера')
    questions = response.json().get('results', None)
    if not questions:
        return EaQuestionResponseStatus(
            success=False,
            data={},
            error='В ответе от сервера отсутствует поле results. '
                  'Отображение списка вопросов невозможно. '
                  'Обратитесь к администратору'
        )
    try:
        data = parse_questions_json(page, questions)
    except RuntimeError:
        return EaQuestionResponseStatus(
            success=False,
            data={},
            error='Произошла ошибка распознавания данных из ЕА'
        )
    return EaQuestionResponseStatus(success=True, data=data)


def parse_questions_json(page, questions):
    questionss = get_concrete_questions_page(questions, page)
    questions_list = [parse_single_question_json(question) for question in questionss]
    result = {'page': page, 'real_count': len(questions), 'questions': questions_list}
    return result


def parse_single_question_json(question):
    current_question = {
        'id': question['id'],
        'date': get_datetime_from_ea_string(question['commented_at']),
        'reason': question['related_text'],
        'first_que': question['preview'],
        'teacher': get_teacher(question)
    }
    return current_question


def open_question(message):
    jsn = get_question_page_json(bot.bot_states.QuestionsState.page).data['questions'][int(message.text) % 5 - 1]
    phrases = requests.get(EAUrls.get_chat_comments_url(jsn['id']),
                           cookies={'eduapp_jwt': config.EDUAPP_JWT}).json()['results']
    return jsn, phrases

