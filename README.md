# Проект "SHP.bot"

### Цель
DEFINE ME!

### Технологический стек:
- Python 3.8
- pyTelegramBotAPI 4.4
- requests 2.27

### Инструкция по настройке проекта:
1. Склонировать проект
2. Открыть проект в PyCharm с наcтройками по умолчанию
3. Создать виртуальное окружение (через settings -> project "shp_bot" -> project interpreter)
4. Открыть терминал в PyCharm, проверить, что виртуальное окружение активировано.
5. Обновить pip:
   ```bash
   pip install --upgrade pip
   ```
6. Установить в виртуальное окружение необходимые пакеты: 
   ```bash
   pip install -r requirements.txt
   ```
   Если требуется окружение для разработки - дополнительно нужно установить пакеты
   ```bash
   pip install -r requirements_dev.txt
   sudo apt install make
   ```
7. Скопируйте и переименуйте файл `.env.sample` в файл `.env`
8. Добавьте в него токен своего бота в переменную `TELEGRAM_BOT_TOKEN`. 
   Как получить токен - читаем здесь: [https://core.telegram.org/bots#botfather](https://core.telegram.org/bots#botfather)
9. Создать конфигурацию запуска в PyCharm (файл `main.py`)
10. Запуск pylint делается так:
   ```bash
   pylint bot eduapp ui *.py
   ```
11. Запуск тестов делается так:
   ```bash
   python tests_runner.py
   ```
