# -*- coding: utf-8 -*-
"""
This file is for  functions that are tied to the background handling of queries.
"""

from uuid import uuid4

import dataset
import itertools
#import emoji

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler
import logging
import datetime

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few query handlers. 


def inlinequery(bot, update):
    """
    responds to requests live like @gif ___
    Returns Transaction details QueryResultArticle from input tokenID

    """
    In_query = update.inline_query.query
    logger.info("got{}".format(In_query))
    
    db = dataset.connect('sqlite:///exportdata/transactions.db')
    table = db['usertransactions']
    
    try:
        found_data = table.find_one(token=In_query)
        amount = found_data['amount']
        reason = found_data['reason']
        logger.info("found in database {}, {}".format(amount,reason))
        nowstring=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        results = list()
        
        In_keyboard = [[InlineKeyboardButton("Yes. Thanks for reminding.", callback_data=In_query+'1')],
                       [InlineKeyboardButton("No. I do not recall this.", callback_data=In_query+'0')]]

    
        if amount <= 0 :
            results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Click Here.\n Amount:{}, Note:{}".format(amount,reason),
                                            reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                            input_message_content=InputTextMessageContent(
                                                "{}\n Hey I owe you {}, for {} \n Please confirm this transaction.".format(nowstring, -amount, reason) )))
        
        elif amount > 0:
            results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Click Here.\n Amount:{}, Note:{}".format(amount,reason),
                                            reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                            input_message_content=InputTextMessageContent(
                                                "{}\n Hey you owe me {}, for {} \n Please confirm this transaction.".format(nowstring, amount, reason) )))

        
    
    except:
        results = list()
        
    
    update.inline_query.answer(results)



def trans_confirmer(bot, update):
    """
    Responds to button presses.

    Choice codes
    0 : Receiver rejects
    1 : Receiver accepts
    2 : Unnecessary clicking

    """
    nowstring=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    query = update.callback_query
    user1n = query.from_user
    user1 = query.from_user.id

    token,choice=query.data[:-1],query.data[-1:]
    logger.info('got token={}, choice={}, from={}'.format(token, choice, user1))

    #if unnecessary clicking
    if choice == '2':        
        logger.info("unnecessary clicking")
        return 
        #---------------------#Terminate function return none--------------------

    #if not unnecessary clicking
    db = dataset.connect('sqlite:///exportdata/transactions.db')
    table = db['usertransactions']


    found_data = table.find(token=token)
    logger.info('found for token {} , {}'.format(token, found_data))
    assert(count_iterable(found_data) == 1)

    found_data = table.find_one(token=token)
    amount = found_data['amount']
    reason = found_data['reason']
    user0  = found_data['sender']
    logger.info('got data amount={}, reason={}, sender={}'.format(amount, reason, user0))
    """
    if choice == '3':
            txt=ourhistory(user0, user1n)
            In_keyboard = [[InlineKeyboardButton("we Osum🤖", url="telegram.me/weOsumBot")],
                            [InlineKeyboardButton("{}".format(txt), callback_data=token+'2')]]

            original_text= ("Hey I owe you {}, for {} \n Please confirm this transaction.".format(-amount, reason) if amount <= 0 else "Hey "
                "you owe me {}, for {} \n Please confirm this transaction.".format( amount, reason) )
            confirm_text= "\nUpdate:{}\nThank you for confirming.\n Update:{}".format(nowstring, txt)

            bot.editMessageText(text=original_text+confirm_text,
                                inline_message_id=update.callback_query.inline_message_id) 
            bot.editMessageReplyMarkup(reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                       inline_message_id=update.callback_query.inline_message_id)
    """
    if user1 == user0:        #if sender itself tries to confirm
        logger.info('{} is a fraud.'.format(user0))
        return
        #---------------------#Terminate function return none--------------------
    
    if found_data['status'] == 'open':
        table.update(dict(token=found_data['token'], receiver=user1), ['token'])     #updates receiver info for transaction in the table
        logger.info('got receiver (and updated in table) {}'.format(user1))
    

    
    #Enforcing Receiver choice.
    
    if choice == '0':           #if receiver rejects
                table.update(dict(token=found_data['token'], status='disputed' ), ['token'])

                In_keyboard = [[InlineKeyboardButton("Confirm. Now I recall it.", callback_data=token+'1')],
                               [InlineKeyboardButton('No. I still do not recall any such transaction.', callback_data=token+'2')]]

                original_text= ("Hey I owe you {}, for {} \nPlease confirm this transaction.\n".format(-amount, reason) if amount <= 0 else "Hey "
                "you owe me {}, for {} \nPlease confirm this transaction.\n".format( amount, reason) ) 

                dispute_text = "\nUpdate:{}\nThis transaction is disputed by you.\nYou can still confirm it after discussion.".format(nowstring)
                bot.editMessageText(text=original_text+dispute_text,
                                    inline_message_id=update.callback_query.inline_message_id) 
                bot.editMessageReplyMarkup(reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                           inline_message_id=update.callback_query.inline_message_id)

    elif choice == '1':         #if receiver confirms
            table.update(dict(token=found_data['token'], status='confirmed' ), ['token'])

            In_keyboard = [[InlineKeyboardButton("we Osum🤖", url="telegram.me/weOsumBot")],
                            [InlineKeyboardButton("Our sum", callback_data=token+'3')]]

            original_text= ("Hey I owe you {}, for {} \n Please confirm this transaction.".format(-amount, reason) if amount <= 0 else "Hey "
                "you owe me {}, for {} \n Please confirm this transaction.".format( amount, reason) )
            confirm_text= "\nUpdate:{}\nThank you for confirming.".format(nowstring)

            bot.editMessageText(text=original_text+confirm_text,
                                inline_message_id=update.callback_query.inline_message_id) 
            bot.editMessageReplyMarkup(reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                inline_message_id=update.callback_query.inline_message_id)
    
    elif choice == '3':
            In_keyboard = [[InlineKeyboardButton("we Osum🤖", url="telegram.me/weOsumBot")]]
            txt=ourhistory(user0, user1n)
            original_text= ("Hey I owe you {}, for {} \nPlease confirm this transaction.\n".format(-amount, reason) if amount <= 0 else "Hey "
                "you owe me {}, for {} \nPlease confirm this transaction.\n".format( amount, reason) )
            confirm_text= "\nUpdate:{}\nThe transaction is confirmed by you.".format(nowstring)

            bot.editMessageText(text=original_text+confirm_text,
                                inline_message_id=update.callback_query.inline_message_id) 
            bot.editMessageReplyMarkup(reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                       inline_message_id=update.callback_query.inline_message_id)                                                                


def ourhistory(user0, user1n):
    fstotal=[]
    frtotal=[]

    logging.info('user1n{}'.format(user1n))
    db = dataset.connect('sqlite:///exportdata/transactions.db')
    table = db['usertransactions']
    #Finding
    #All user0_owes
    user_sent = table.find(sender=str(user1n.id))
    #All user0_isowed
    user_got = table.find(receiver=str(user1n.id))
    #Merge the finds

    for row in user_sent:
        if row['receiver']==user0 and row['status']=="confirmed":
            fstotal.append(row['amount'])
            logging.info('user1 s and user0 r amount : {}'.format(row['amount']))
    for row in user_got:
        if row['sender']==user0 and row['status']=="confirmed":
            frtotal.append(row['amount'])
            logging.info('user1 r and user0 s amount : {}'.format(row['amount']))
    decamount=sum(fstotal)-sum(frtotal)
    nowstring=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    if decamount>=0:
        sts='as on {} : I owe you : ₹{}'.format(nowstring, abs(decamount))
    else:
        sts='as on {} : You owe me : ₹{}'.format(nowstring, abs(decamount))
    return sts

def count_iterable(i):
    return sum(1 for e in i)