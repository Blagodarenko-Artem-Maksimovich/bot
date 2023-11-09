import logging
import re
from datetime import datetime

import bot.bot_states
import bot.handlers

from ui.calendar import CalendarUI


def input_date_period(message, tele_bot, bot_status):
    result = process_date_period(message, bot_status, tele_bot)
    if result['success']:
        bot.handlers.HandlerStructure(message, tele_bot, bot_status, bot.bot_states.CalendarState)
        return
    tele_bot.send_message(message.chat.id, result['message'])
    tele_bot.register_next_step_handler(message, input_date_period)


def process_date_period(message, bot_status, tele_bot):
    result = {
        'success': False,
        'message': None,
        'repeat': True,
    }
    format_check = re.search(r'\d{2}\.\d{2}-\d{2}\.\d{2}', message.text)
    if not format_check:
        result['message'] = CalendarUI.ERROR_INVALID_INPUT_FORMAT
        return result
    start_date, end_date = get_calendar_dates(message.text)
    if start_date is None:
        result['message'] = CalendarUI.ERROR_INVALID_DAY
        return result
    if start_date > end_date:
        result['message'] = CalendarUI.ERROR_INVALID_START
        return result
    bot.handlers.CalendarCommandHandler(
        message=message,
        t_bot=tele_bot,
        status_of_bot=bot_status,
        start_date=start_date,
        end_date=end_date
    )
    result['success'] = True
    return result


def get_calendar_dates(text):
    dates = re.findall(r'\d{2}\.\d{2}', text)
    start_date = end_date = None
    if len(dates) != 2:
        return start_date, end_date
    try:
        start_date = get_date_from_str(dates[0])
        end_date = get_date_from_str(dates[1])
    except ValueError:
        logging.warning('Ошибка декодирования даты из строки: %s', str(dates))
    return start_date, end_date


def get_date_from_str(date):
    return datetime.strptime(date, '%d.%m').replace(year=datetime.now().year)
