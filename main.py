# -*- coding: utf-8 -*-

import queryhandlers     #custom queryhandlers file
from commands import *   #functions defined for bot commands

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler

import logging
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


import dataset
# connecting to a SQLite database and get a reference to the table 'transactions'
db = dataset.connect('sqlite:///exportdata/transactions.db')
table = db['usertransactions']


def main():
    
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("215450926:AAELiS1y9NIczfgy19KO48mnlMVrcf4xVCs")    #tokenHg
    #updater = Updater("292385752:AAFCJrNmm_x47FFk_VzJqQFToDnZ7BdQKCU")    #tokenOsum
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('iOsum',    iOsum,    pass_user_data=True),
                      CommandHandler('theyOsum', theyOsum, pass_user_data=True),
                      CommandHandler('heOsum',   theyOsum, pass_user_data=True),
                      CommandHandler('sheOsum',  theyOsum, pass_user_data=True), ],

        states={
            PROCESSAMOUNT: [MessageHandler(Filters.text, process_amount, pass_user_data=True)],
            
            CONFIRMAMOUNT: [RegexHandler('^(Yes|No)$', confirmerAmount, pass_user_data=True)],
            
            PROCESSREASON: [MessageHandler(Filters.text, process_reason, pass_user_data=True)],
            
            CONFIRMREASON: [RegexHandler('^(Yes|No)$', confirmerReason, pass_user_data=True)],
            
            GENERATETOKEN: [MessageHandler(Filters.text, token, pass_user_data=True)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('history', history))
    dp.add_handler(CommandHandler('cancel', cancel))
    #dp.add_handler(CallbackQueryHandler(calci))

    #QueryHandlers
    dp.add_handler(InlineQueryHandler(queryhandlers.inlinequery))
    dp.add_handler(CallbackQueryHandler(queryhandlers.trans_confirmer))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print('Started Bot')

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    
    #Export collected data
    logger.info("Exiting. Saving collected data")
    db = dataset.connect('sqlite:///exportdata/transactions.db')
    table = db['usertransactions']
    dataset.freeze(table, format='json', filename='transactions.json')
    print('Bye')



if __name__ == '__main__':
    main()
    
    
