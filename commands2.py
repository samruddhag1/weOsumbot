# -*- coding: utf-8 -*-
"""
This file is for  functions that are directly tied to the bot commands.
"""

from numpy import random as nprandom
import queryhandlers        #custom queryhandlers file

from asteval import Interpreter
aeval = Interpreter()       #Using this instead of eval

import itertools
#import emoji

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardHide)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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


CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

PROCESSAMOUNT, CONFIRMAMOUNT, PROCESSREASON, CONFIRMREASON, GENERATETOKEN, INLINESELECT = range(6)



def start(bot , update): 
    s="Lets get you started!\n"
    s+="You can use any of these commands\n"
    s+="/iOsum   : You know you owe them. Use this to keep track. \n"
    s+="/heOsum  : He owes you. Lets confirm this and keep track. \n"
    s+="/sheOsum : She owe you. Lets confirm this and keep track. \n\n"

    s+="/history : Does what is said. Opens your history book. Study! \n"

    update.message.reply_text(s)


def iOsum(bot , update, user_data):
    """
    Osum converstion starts.
    """
    update.message.reply_text(
        'Hi! Looks like you owe somebody. '
        'I will help you remember your dues.'
        'Send /cancel to stop talking to me.\n\n')
    
    user_data['amount']   = None
    user_data['reason']   = None
    user_data['who_owes'] = "iOsum"
    logger.info('/iOsum by user: {}'.format(update.message.from_user))
    return askAmount(bot, update)


def theyOsum(bot , update, user_data):
    """
    Osum converstion starts.
    """
    update.message.reply_text(
        'Hi! Looks like somebody owes you. '
        'I will help you remember their dues.'
        'Send /cancel to stop talking to me.\n\n')
    
    user_data['amount']   = None
    user_data['reason']   = None
    user_data['who_owes'] = "theyOsum"
    logger.info('/theyOsum by user: {}'.format(update.message.from_user))
    return askAmount(bot, update)


def askAmount(bot, update):
    """
    - Asks user for amount.
    - Changes state to PROCESSAMOUNT when done 
    """
    update.message.reply_text(
        'Please enter the transaction Amount: ')
    
    logger.info(' user: {} entering amount'.format(update.message.from_user))
    
    return PROCESSAMOUNT

def verify_amount(str_amt):
    """
    - Verifies if amount is valid.
    """
    logger.info('Verifing: {}'.format(str_amt))
    try :
        amount = aeval(str_amt)     #using asteval's Interpreter as aeval
    except :
        amount = None
        logger.info('Invalid Amount: {}'.format(str_amt))
    
    return amount


def process_amount(bot, update, user_data):
    """
    - Verifies if amount is valid. If not redo
    - Adds amount to userdata.
    - Changes state to PROCESSREASON 
    """
    user = update.message.from_user
    amount = verify_amount(update.message.text)
    if amount is not None:
        logger.info('Valid Amount: {}'.format(update.message.text))
        logger.info("User:{} Amount: {}".format(user, amount))

        if user_data['who_owes'] == "iOsum":
            amount = -amount

        user_data['amount'] = amount
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
        'Transaction Amount {}\n Confirm?'.format(amount),
         reply_markup=ReplyKeyboardMarkup([['Yes','No']], one_time_keyboard=True))
    
    return CONFIRMAMOUNT
    
def confirmerAmount(bot, update, user_data):
    """
    Depending on user response:
    passes control forward 
    or loopback to askAmount.
    """
    response = update.message.text
    user = update.message.from_user
    if response == 'No':
        logger.info('user: {} chooses to redo askAmount'.format(user))
        return askAmount(bot, update)
        
    elif response == 'Yes':
        logger.info('user: {} confirmed amount. Moving on..'.format(user))
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
    
    logger.info('user: {} is now reasoning'.format(update.message.from_user))
    return PROCESSREASON

def process_reason(bot, update, user_data):
    """
    Recieves transaction notes. 
    """
    reason = update.message.text
    if reason == 'skip':
        reason = ''
    
    user_data['reason'] = reason
    return confirmReason(bot, update, reason)

def confirmReason(bot, update, reason):
    """
    -Asks user to confirm reason
    """
    update.message.reply_text(
        'Reason for the transaction : {!r}\n Confirm?'.format(reason),
         reply_markup=ReplyKeyboardMarkup([['Yes','No']], one_time_keyboard=True))
         
    return CONFIRMREASON

def confirmerReason(bot, update, user_data):
    """
    Depending on user response:
    Saves reason to user_data and passes control forward 
    or loopback to askReason.
    """
    response = update.message.text
    if response == 'No':
        return askReason(bot, update)
        
    elif response == 'Yes':
        return token(bot, update, user_data)


def token(bot, update, user_data):
    """
    Generates a transaction tokenid

    status can have 3 states
    =open
    =confirmed
    =rejected
    """
    user = update.message.from_user
    # connecting to the SQLite database and get a reference to the table 'transactions'
    db = dataset.connect('sqlite:///exportdata/transactions.db')
    table = db['usertransactions']

    current_trans = dict(sender=user.id, amount=user_data['amount'], reason=user_data['reason'], status='open' )
    tid = table.insert(current_trans)
    
    token= 'O{:.3}{:0>6}'.format(user.first_name,tid)
    table.update(dict(id=tid, token=token, receiver='Unknown'), ['id'])
    
    logger.info("generated token:{}".format(token) )

    return friend_selector(bot, update, token, current_trans)   


def friend_selector(bot, update, token, current_trans):
    In_keyboard = [[InlineKeyboardButton("Confirm with friend?", switch_inline_query=token)]]
    In_reply_markup = InlineKeyboardMarkup(In_keyboard)

    current_trans['absamount'] = abs(current_trans['amount'])

    if current_trans['amount'] <= 0 :
        update.message.reply_text('You owe {absamount} for {reason} reason, now choose a friend to confirm this transaction.'.format(**current_trans), 
            reply_markup=In_reply_markup)

    elif current_trans['amount'] >0 :
        update.message.reply_text('Your friend owes {amount} for {reason} reason, now choose a friend to confirm this transaction.'.format(**current_trans), 
            reply_markup=In_reply_markup)

    
    return ConversationHandler.END


def history(bot, update):
    """
    Returns history of transacion
    """
    user = update.message.from_user
    # connecting to the SQLite database and get a reference to the table 'transactions'
    db = dataset.connect('sqlite:///exportdata/transactions.db')
    table = db['usertransactions']

    logger.info("serving user= {} a history lesson".format(user) )
    
    #Finding
    #All user0_owes
    user_sent = table.find(sender=user.id)
    #All user0_isowed
    user_got = table.find(receiver=user.id)
    #Merge the finds
    user_all=itertools.chain(user_sent,user_got)
    
    update.message.reply_text(lesson(user_all),
                            reply_markup=ReplyKeyboardRemove())


def lesson(sublist):
    """
    Makes the history lesson string.
    """
    s=''
    i=1
    toatal=[]
    for row in sublist:
        if row['status']=='confirmed':
           row['status']= u"\u2713"
           toatal.append(row['amount'])
        elif row['status']=='disputed':
            row['status']= u"\u2718"
        else:
            row['status']="🤷‍♀"
        if row['amount']<0:
            row['amount']=abs(row['amount'])
            s+="{}. {receiver}  »—  ₹{amount}  -→  {sender}, {status} \n".format(i, **row)
        else:
            s+="{}. {sender}  »—  ₹{amount}  -→  {receiver}, {status} \n".format(i, **row)
        i+=1
    s+="Total Balance : {} \n".format(sum(toatal))
    return s

#Printing out database subtable
def subtable2str(table,sublist):
    s=''
    for item in table.columns:
        s+= str(item)+'\t'   #Printing headers
    s+='\n'
    
    for row in sublist:
        for item in table.columns:
            s+=str(row[item]) + '\t'  #Printing values
        s+='\n'

    return s


    
    
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
    #updater = Updater("215450926:AAELiS1y9NIczfgy19KO48mnlMVrcf4xVCs")    #tokenHg
    updater = Updater("292385752:AAFCJrNmm_x47FFk_VzJqQFToDnZ7BdQKCU")    #tokenOsum
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