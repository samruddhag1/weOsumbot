# -*- coding: utf-8 -*-
"""
Calculator @Telegram
"""
from asteval import Interpreter
aeval = Interpreter()       #Using this instead of eval

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


In_reply_keyboard = [[InlineKeyboardButton("7",callback_data='7'),
                      InlineKeyboardButton("8",callback_data='8'),
                      InlineKeyboardButton("9",callback_data='9'),
                      InlineKeyboardButton("+",callback_data='+')],
                     [InlineKeyboardButton("4",callback_data='4'),
                      InlineKeyboardButton("5",callback_data='5'),
                      InlineKeyboardButton("6",callback_data='6'),
                      InlineKeyboardButton("-",callback_data='-'),],
                     [InlineKeyboardButton("1",callback_data='1'),
                      InlineKeyboardButton("2",callback_data='2'),
                      InlineKeyboardButton("3",callback_data='3'),
                      InlineKeyboardButton("*",callback_data='*')],
                     [InlineKeyboardButton(".",callback_data='.'),
                      InlineKeyboardButton("0",callback_data='0'),
                      InlineKeyboardButton("(",callback_data='('), 
                      InlineKeyboardButton(")",callback_data=')')],
                     [InlineKeyboardButton("Del",callback_data='Del'),
                      InlineKeyboardButton("=",callback_data='=')],
                     [InlineKeyboardButton("CLEAR",callback_data='CLEAR'),
                      InlineKeyboardButton("Done",callback_data='Done')]]

calc_markup = InlineKeyboardMarkup(In_reply_keyboard, one_time_keyboard=False)

def start(bot, update):
    """
    - Asks user for amount.
    - Changes state to PROCESSAMOUNT when done 
    """
    update.message.reply_text(
        'What shall we compute?')
    
    update.message.reply_text(
        'Please use the buttons to enter Amount: ',
        reply_markup=calc_markup)
    
    logger.info(' user: {} starts playing with calci'.format(update.message.from_user))
    

def calci(bot, update):
    query = update.callback_query
    text = query.message.text
    user = query.message.from_user
    
    if (query.data == '='):
        
        str_amt = text.replace('Please use the buttons to enter Amount:','')
        str_amt = str_amt.strip(' ')   #remove unnecessary spaces
        amount = verify_amount(str_amt)
        if amount is not None:
            bot.editMessageText(text="Please use the buttons to enter Amount: {}".format(amount),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id ,reply_markup=calc_markup)    
        else:
             bot.editMessageText(text="Please use the buttons to enter Amount: INVALID",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id,reply_markup=calc_markup)
    elif (query.data == 'Del'):
        bot.editMessageText(text=text[:-1],
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id ,reply_markup=calc_markup)
    elif(query.data == 'CLEAR'):
        amount = ''
        
        bot.editMessageText(text="Please use the buttons to enter Amount: {}".format(amount),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id ,reply_markup=calc_markup)
        
    elif (query.data == 'Done'):
        str_amt = text.replace('Please use the buttons to enter Amount:','')
        str_amt = str_amt.strip(' ')   #remove unnecessary spaces
        amount = verify_amount(str_amt)
        if amount is not None:
            bot.editMessageText(text="Amount: {}".format(amount),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id) 
            
            logger.info("User {} Done with entering amount.".format(user))
            return amount
        
        else :
            bot.editMessageText(text="Please use the buttons to enter Amount: INVALID",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id,reply_markup=calc_markup)
        
        
    else:  
        bot.editMessageText(text=text+"{}".format(query.data),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id ,reply_markup=calc_markup)

def verify_amount(str_amt):
    """
    - Verifies if amount is valid.
    """
    logger.info('Verifing: {}'.format(str_amt))
    try :
        amount = aeval(str_amt)     #using asteval's Interpreter as aeval
        logger.info('Valid Amount: {}'.format(str_amt))
    except :
        amount = None
        logger.info('Invalid Amount: {}'.format(str_amt))
    
    return amount
    
def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))
    
def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("215450926:AAELiS1y9NIczfgy19KO48mnlMVrcf4xVCs")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add handler for start and calci

    dp.add_handler(CommandHandler('start', start))

    dp.add_handler(CallbackQueryHandler(calci))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    print('Started Bot')

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()