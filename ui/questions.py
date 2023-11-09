from jinja2 import Environment, PackageLoader, select_autoescape

import bot.bot_states
import config
from ui.main import get_template_to_html


def question_page_to_str(jsn):
    template = get_template_to_html('question_list.html')
    questions = []
    for i in range(len(jsn['questions'])):
        current_question = jsn['questions'][i]
        question = {
            'number': i + jsn["page"] * 5 - 4,
            'theme': current_question["reason"],
            'first': current_question["first_que"],
            'teacher': current_question["teacher"],
            'data': current_question["date"]
        }
        questions.append(question)
    context = {
        'questions': questions
    }
    return template.render(context)


def single_question_to_str(jsn, phrases):
    template = get_template_to_html('single_question.html')
    comments = []
    for phrase in phrases:
        phrase_context = {
            'is_author_you': phrase['author']['username'] == config.USER_LOGIN,
            'message': phrase['message']
        }
        comments.append(phrase_context)

    context = {
        'theme': jsn["reason"],
        'teacher': jsn["teacher"],
        'date': jsn["date"],
        'is_many_comments': False,
        'comments': comments
    }
    if len(context['comments']) > 10:
        context['comments'] = context['comments'][-10 * bot.bot_states.QueChatState.page: -10 * (bot.bot_states.QueChatState.page - 1)]
        context['is_many_comments'] = True

    return template.render(context)
