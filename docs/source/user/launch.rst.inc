Запуск приложения
~~~~~~~~~~~~~~~~~

Подготовка к запуску
^^^^^^^^^^^^^^^^^^^^

**Технологический стек**:

- Python 3.8
- pyTelegramBotAPI 4.4
- requests 2.27

**Инструкция по настройке проекта**:

#. Открыть проект в PyCharm с наcтройками по умолчанию
#. Создать виртуальное окружение (через ``settings`` -> ``project "shp_bot"`` -> ``project interpreter``)
#. Открыть терминал в PyCharm, проверить, что виртуальное окружение активировано.
#. Обновить pip:

   .. code-block:: console

      pip install --upgrade pip


#. Установить в виртуальное окружение необходимые пакеты:

   .. code-block:: console

      pip install -r requirements.txt

   Если требуется окружение для разработки - дополнительно нужно установить пакеты:

   .. code-block:: console

      pip install -r requirements_dev.txt
      sudo apt install make


Получение токена
^^^^^^^^^^^^^^^^

#. Зайти на сайт |tg_botfather_link|.
#. Следуя инструкции на сайте, создать нового бота и получить токен
#. В проекте скопировать и переименовать файл ``.env.sample`` в файл ``.env``
#. Вставить полученный токен в этот файл в переменную ``TELEGRAM_BOT_TOKEN``

.. |tg_botfather_link| raw:: html

   <a href="https://core.telegram.org/bots#botfather" target="_blank">https://core.telegram.org/bots#botfather</a>

Запуск бота
^^^^^^^^^^^
* Запустить файл ``main.py``
* Начать диалог с ботом командой `/start`
