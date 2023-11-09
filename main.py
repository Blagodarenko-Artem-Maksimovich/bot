import logging

import bot.main


def main():
    fmt = '[%(levelname)s] %(asctime)s: %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt)
    bot.main.tele_bot.infinity_polling()


if __name__ == '__main__':
    main()
