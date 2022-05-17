import os
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater
from dotenv import load_dotenv
from utils import get_logger
import json
from pprint import pprint
from const import FORBIDDEN

logger = get_logger('bot.py', 'log.txt')

load_dotenv(dotenv_path='.env')
TOKEN = os.getenv("token")
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def collect_urls(message_data):
    urls = list()
    for dct in message_data['entities']:
        if 'url' in dct:
            urls.append(dct['url'])

    return urls


def delete_message(context, chat_id, message_id, message_data):
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    logger.info(f"deleted: {json.dumps(message_data, ensure_ascii=False, indent=4)}")


def foo(update: Update, context: CallbackContext):
    message_data = update.message.to_dict()
    pprint(message_data)
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    urls = collect_urls(message_data)

    for forbidden in FORBIDDEN:
        if 'text' in message_data and forbidden in message_data['text']:
            delete_message(context, chat_id, message_id, message_data)

        for url in urls:
            if forbidden in url:
                delete_message(context, chat_id, message_id, message_data)
                break

    if 'text' in message_data and message_data['text'] == '/log':
        context.bot.sendDocument(chat_id=chat_id,
                                 caption="logfile", document=open('log.txt', 'rb'))

    # if 'new_chat_members' in message_data and len(message_data['new_chat_members']) > 0:
    # smth strange happens. During tests chat opens more slowly. That's a bad sign, so disabling it.
    #     delete_message(context, chat_id, message_id, message_data)


mh = MessageHandler(Filters.all, foo)
dispatcher.add_handler(mh)
updater.start_polling()
