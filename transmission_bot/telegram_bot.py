import logging
import logging.handlers
from telegram.ext import (Updater,
                          CommandHandler,
                          MessageHandler,
                          )
from broker import TransmissionBroker
from transmissionrpc.error import TransmissionError

from cfg import TOKEN

HELP_TEXT = """Transmission Telegram bot
Usage:
/help - display this help
/list - retrieve list of current torrents and their statuses
/add <URI> - add torrent and start download
"""


logger = logging.getLogger()
logger.setLevel(logging.INFO)
global_broker = TransmissionBroker()
global_updater = Updater(token=TOKEN)


def transmission_error(bot, update, exception):
    """send error to chat and exit."""
    error_message = f"Transmission exception happened:\n{exception}"
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=error_message)
    logging.error(error_message)


def telegram_error(bot, update, error):
    """Send error to syslog and exit."""
    error_message = f'Update "{update}" caused error "{error}"'
    logging.error(error_message)


def help_command(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=HELP_TEXT)


def add_command(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text="Adding torrent to Transmission")

    try:
        global_broker.add_torrent(
            update.message.chat_id, update.message.text.split(' ', 1)[1])

        bot.sendMessage(chat_id=update.message.chat_id,
                        text="Torrent successfully added")
    except TransmissionError as e:
        transmission_error(bot, update, e)


def list_command(bot, update):
    try:
        torrents = global_broker.retrieve_list(update.message.chat_id)
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=f"Here are current torrents list:\n{torrents}")
    except TransmissionError as e:
        transmission_error(bot, update, e)


def start_bot():
    logging.info('Starting bot')

    dispatcher = global_updater.dispatcher
    dispatcher.add_error_handler(telegram_error)

    list_handler = CommandHandler('list', list_command)
    dispatcher.add_handler(list_handler)

    add_handler = CommandHandler('add', add_command)
    dispatcher.add_handler(add_handler)

    help_handler = CommandHandler('help', help_command)
    dispatcher.add_handler(help_handler)

    start_handler = CommandHandler('start', help_command)
    dispatcher.add_handler(start_handler)

    global_updater.start_polling()


def main():
    start_bot()


if __name__ == '__main__':
    main()
