class MonthNames:
    january = 'Январь'
    february = 'Февраль'
    march = 'Март'
    april = 'Апрель'
    may = 'Май'
    june = 'Июнь'
    july = 'Июль'
    august = 'Август'
    september = 'Сентябрь'
    october = 'Октябрь'
    november = 'Ноябрь'
    december = 'Декабрь'

    @staticmethod
    def translate(name):
        if name in MonthNames.__dict__:
            return MonthNames.__dict__[name]
        return ''


class LessonStatusSymbols:
    SYMBOLS = {
        'Посещено': '🟢',
        'Пропущено': '🔴',
        'Предстоит': '⚪'
    }
    VISITED = SYMBOLS['Посещено']
    MISSED = SYMBOLS['Пропущено']
    PLANNED = SYMBOLS['Предстоит']

    @staticmethod
    def translate(name):
        if name in LessonStatusSymbols.SYMBOLS:
            return LessonStatusSymbols.SYMBOLS[name]
        return ''
