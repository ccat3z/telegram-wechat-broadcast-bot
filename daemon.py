from telegram.ext import Updater
from telegram.ext import (CommandHandler, MessageHandler,
                          ConversationHandler, RegexHandler)
from telegram.ext import Filters

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

from urllib.request import Request, urlopen
from urllib.parse import urlencode

import logging
from logging.config import dictConfig
import argparse

# set up logger
logging_config = dict(
    version = 1,
    formatters = {
        'f': {
            'format': '%(asctime)s [%(levelname)s] %(message)s'
        }
    },
    handlers = {
        'h': {
            'class': 'logging.StreamHandler',
            'formatter': 'f',
            'level': logging.INFO
        }
    },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG
    })
dictConfig(logging_config)

# parse arguments
parser = argparse.ArgumentParser(prog='tele-wxbot',
                                 description='WeChat broadcast bot on Telegram')
parser.add_argument('-t', '--token', help = 'bot token',
                    required = True)

args = parser.parse_args()

token = args.token
sckey = {}

debug = True

gbot = None
gupdate = None

updater = Updater(token=token)
dispatcher = updater.dispatcher

SC_KEY, = range(1)

def send_img(uid, sckey, url):
    """Send image

    Parameters
    ----------
    uid
        Unique id of this message
    sckey
        SCKEY of FT
    url
        URL of the image
    """

    data = urlencode({
        'text': "WeChat Broadcast from Telegram",
        'desp': str(uid) + '\n' + url
    }).encode()
    urlopen(Request("https://sc.ftqq.com/" + sckey + ".send", data))

def start(bot, update):
    update.message.reply_text('Welcome! Please select a boardcast.')
    update.message.reply_text(
        'But you have no choice, we only support Server酱 for now.'
    )
    update.message.reply_text('Please enter your sckey')

    return SC_KEY

def get_sc_key(bot, update):
    sckey[update.message.chat.id] = update.message.text
    update.message.reply_text(
        'Done. Your sckey is ' + sckey[update.message.chat.id]
    )

    return ConversationHandler.END

def sticker(bot, update):
    url = updater.bot.getFile(update.message.sticker.file_id).file_path
    try:
        send_img(update.message.date,
                 sckey=sckey[update.message.chat.id], url='![](' + url + ')')
        update.message.reply_text("Got it!")
    except KeyError:
        update.message.reply_text("/start first")

    if debug:
        global gbot, gupdate
        gbot = bot
        gupdate = update

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        SC_KEY: [MessageHandler(Filters.text, get_sc_key)]
    },
    fallbacks=[]
)

dispatcher.add_handler(conv_handler)
dispatcher.add_handler(MessageHandler(Filters.sticker, sticker))

updater.start_polling()
