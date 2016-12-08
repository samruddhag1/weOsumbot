# -*- coding: utf-8 -*-
"""
This file is for  functions that are directly tied to the bot commands.
"""

from numpy import random as nprandom
from asteval import Interpreter
aeval = Interpreter()       #Using this instead of eval

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardHide)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, CallbackQueryHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

PROCESSAMOUNT, CONFIRMAMOUNT, PROCESSREASON, CONFIRMREASON, GENERATETOKEN, INLINESELECT = range(6)

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

def calci(bot, update):
    query = update.callback_query
    text = query.message.text
    
    if (query.data == '='):
        
        str_amt = text.replace('Please enter the transaction Amount:','')
        amount = verify_amount(str_amt)
        
        bot.editMessageText(text="Please enter the transaction Amount: {}".format(amount),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id ,reply_markup=calc_markup)    
  
    elif (query.data == 'Del'):
        bot.editMessageText(text=text[:-1],
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id ,reply_markup=calc_markup)
    elif(query.data == 'CLEAR'):
        amount = ''
        
        bot.editMessageText(text="Please enter the transaction Amount: {}".format(amount),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id ,reply_markup=calc_markup)
        
    elif (query.data == 'Done'):
        str_amt = text.replace('Please enter the transaction Amount:','')
        amount = verify_amount(str_amt)
        if amount:
            bot.editMessageText(text="Amount: {}".format(amount),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id) 
            return askReason(bot, update)
        
        else :
            bot.editMessageText(text="Please enter the transaction Amount: INVALID",
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id,reply_markup=calc_markup)
            
        
    else:  
        bot.editMessageText(text=text+"{}".format(query.data),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id ,reply_markup=calc_markup)


def iOsum(bot , update):
    """
    Osum converstion starts.
    """
    update.message.reply_text(
        'Hi! Looks like you owe somebody. '
        'I will help you remember your dues'
        'Send /cancel to stop talking to me.\n\n')
    
    logger.info('/iOsum by user: {}'.format(update.message.from_user))    
    return askAmount(bot, update)


def askAmount(bot, update):
    """
    - Asks user for amount.
    - Changes state to PROCESSAMOUNT when done 
    """
    update.message.reply_text(
        'How much exactly do you owe?')
    
    update.message.reply_text(
        'Please enter the transaction Amount: ',
        reply_markup=calc_markup)
    
    
        
    return PROCESSREASON


def verify_amount(str_amt):
    """
    - Verifies if amount is valid.
    """
    logger.info('Verifing: {}'.format(str_amt))
    try :
        amount = aeval(str_amt)     #using asteval's Interpreter as aeval
        logger.info('Valid Amount: {}'.format(str_amt))
    except :
        amount = False
        logger.info('Invalid Amount: {}'.format(str_amt))
    
    return amount


def process_amount(bot, update):
    """
    - Verifies if amount is valid.
    - If not redo
    - Adds it to userdata.
    - Changes state to PROCESSREASON 
    """
    user = update.message.from_user
    amount = verify_amount(update.message.text)
    print('Here!')
    if amount:
        logger.info("User:{} Amount: {}".format(user, amount))
        
        return confirmAmount(bot, update, amount)
    else:
        update.message.reply_text('Sorry! I could not understand that.')
        logger.info("Asking {} amount again".format(user) )  
        
        return askAmount(bot, update)


def confirmAmount(bot, update, amount):
    """
    - Asks user to confirm amount.
    """
    update.message.reply_text(
        'You owe {}\n Confirm?'.format(amount),
         reply_markup=ReplyKeyboardMarkup([['Yes','No']], one_time_keyboard=True))
    
    return CONFIRMAMOUNT
    
def confirmerAmount(bot, update):
    """
    
    """
    response = update.message.text
    if response == 'No':
        return askAmount(bot, update)
        
    elif response == 'Yes':
        return askReason(bot, update)

def askReason(bot, update):
    """
    - Asks for O reason
    """
    if (update.message is None):
        query = update.callback_query
        chat_id = chat_id=query.message.chat_id
    else :
        chat_id = update.message.chat_id
        
    bot.sendMessage(chat_id=chat_id, 
                        text=
                        'Any reason for this owe?'
                        'Type reason or press skip to skip',
                        reply_markup=ReplyKeyboardMarkup([['skip']], one_time_keyboard=True))
    
    
    return PROCESSREASON
    
def process_reason(bot, update):
    """
    
    """
    reason = update.message.text
    if reason == 'skip':
        reason = ''
    return confirmReason(bot, update, reason)

def confirmReason(bot, update, reason):
    """
    -Asks user to confirm reason
    """
    update.message.reply_text(
        'You owe because: {}\n Confirm?'.format(reason),
         reply_markup=ReplyKeyboardMarkup([['Yes','No']], one_time_keyboard=True))
         
    return CONFIRMREASON


def confirmerReason(bot, update):
    """
    
    """
    response = update.message.text
    if response == 'No':
        return askReason(bot, update)
        
    elif response == 'Yes':
        return token(bot, update)
        
        
        
def token(bot, update):
    """
    """
    t=nprandom.random()*1000
    t=str(int(t))
    transid=str(update.message.from_user.first_name[0])+'O'+t+str(update.message.from_user.id)
    
    logger.info("generated token:{}".format(transid) )
    return friend_selector(bot, update, transid)   
    
def friend_selector(bot, update, transid):
    In_keyboard = [[InlineKeyboardButton("Confirm with friend?", switch_inline_query=transid)]]

    In_reply_markup = InlineKeyboardMarkup(In_keyboard)

    update.message.reply_text('You owe {} for {} reason, now choose a friend to confirm this transaction.', reply_markup=In_reply_markup)
    
    return ConversationHandler.END
'''
def inlineSelect(bot, update):
    query = update.inline_query.query
    results = list()
    In_keyboard = [[InlineKeyboardButton("Confirm", switch_inline_query_current_chat='So kind of you, I fear I had almost forgot that')],
                   [InlineKeyboardButton("Reject", switch_inline_query_current_chat='So kind of you but I do not remember any such trasaction.')]]
    
    results.append(InlineQueryResultArticle(id=uuid4(),
                                            title=query, 
                                            reply_markup=InlineKeyboardMarkup(In_keyboard),
                                            input_message_content=InputTextMessageContent('I owe you {} for {}, please confirm.'),
                                            description='This {} will be maintained by @weOsumBot. I will pay you later.'.format(query)
                                                                        ))
    return ConversationHandler.END
 '''       
def cancel(bot, update):
    user = update.message.from_user
    logger.info("User {} canceled the conversation.".format(user))
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardHide())

    return ConversationHandler.END

def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("215450926:AAELiS1y9NIczfgy19KO48mnlMVrcf4xVCs")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('iOsum', iOsum)],

        states={
            PROCESSAMOUNT: [MessageHandler(Filters.text, process_amount)],
            
            CONFIRMAMOUNT: [RegexHandler('^(Yes|No)$', confirmerAmount)],
            
            PROCESSREASON: [MessageHandler(Filters.text, process_reason)],
            
            CONFIRMREASON: [RegexHandler('^(Yes|No)$', confirmerReason)],
            
            GENERATETOKEN: [MessageHandler(Filters.text, token)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)
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