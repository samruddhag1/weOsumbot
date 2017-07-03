# -*- coding: utf-8 -*-
"""
This file is for  functions that are tied to the background handling of queries.
"""

from uuid import uuid4

import dataset
import datetime

from telegram import InlineQueryResultArticle, ParseMode, \
    InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackQueryHandler
import logging

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
    nowstring=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    try:
        found_data = table.find_one(token=In_query)
        amount = found_data['amount']
        reason = found_data['reason']
        logger.info("found in database {}, {}".format(amount,reason))
        nowstring=datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        results = list()
        
        In_keyboard = [[InlineKeyboardButton("Yes. Thanks for reminding.", callback_data=In_query+'1')],
                       [InlineKeyboardButton("No. I do not recall this.", callback_data=In_query+'0')]]

    
             
        results.append(InlineQueryResultArticle(id=uuid4(),
                                            title="Click Here.\n Amount:{}, Reason:{}".format(amount,reason),
                                            reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                            input_message_content=InputTextMessageContent(
                                                "{}\n Hey I owe you {}, for {} \n Please confirm this transaction.".format(nowstring, amount, reason) )))
        
    
    except:
        results = list()
        
    
    update.inline_query.answer(results)



def trans_confirmer(bot, update):
    """
    Responds to button presses.

    """

    #logger.info('got update {}'.format(update))
    query = update.callback_query
    #logger.info('got callbackquery {} enter?{}'.format(query,query is '0'))
    user1 = query.from_user.id
    logger.info('got user {}'.format(user1))

    if query.data != '2':
        token,choice=query.data[:-1],query.data[-1:]
        logger.info('got {}, {}'.format(token, choice))
        db = dataset.connect('sqlite:///exportdata/transactions.db')
        table = db['usertransactions']    
        found_data = table.find_one(token=token)
        amount = found_data['amount']
        reason = found_data['reason']
        user0 = found_data['sender']
        logger.info('got {}, {}, {}'.format(amount, reason, user0))
        
        if user1 == user0:
            logger.info('{} is an asshole.'.format(user0))
            pass
        elif choice == '0':           #only if receiver confirms
                    In_keyboard = [[InlineKeyboardButton("Confirm. Now I recall it.", callback_data=token+'1')],
                                   [InlineKeyboardButton('No. I do not recall any such transaction.', callback_data='2')]]
                        #bot.editMessageCaption(text="This transaction request with amount:{} for reason:{} is confirmed.".format(amount, reason),
         #                       inline_message_id=update.callback_query.inline_message_id)
                    bot.editMessageText(text="The transaction of {} for {} is rejected.".format(amount, reason),
                                        inline_message_id=update.callback_query.inline_message_id) 
                    bot.editMessageReplyMarkup(reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                               inline_message_id=update.callback_query.inline_message_id)
        #bot.editMessageCaption(inline_message_id=update.callback_query.inline_message_id)
        #bot.editMessageText(inline_message_id=update.callback_query.inline_message_id)
        #bot.editMessageReplyMarkup(inline_message_id=update.callback_query.inline_message_id)
        elif choice == '1':
               #only if receiver confirms
                In_keyboard = [[InlineKeyboardButton("You are Osum!", callback_data='2')]]
        #bot.editMessageCaption(text="This transaction request with amount:{} for reason:{} is confirmed.".format(amount, reason),
         #                       inline_message_id=update.callback_query.inline_message_id)
                bot.editMessageText(text="The transaction of {} for {} is confirmed.".format(amount, reason),
                                    inline_message_id=update.callback_query.inline_message_id) 
                bot.editMessageReplyMarkup(reply_markup=InlineKeyboardMarkup(In_keyboard, one_time_keyboard=False),
                                           inline_message_id=update.callback_query.inline_message_id)
        #bot.editMessageCaption(inline_message_id=update.callback_query.inline_message_id)
        #bot.editMessageText(inline_message_id=update.callback_query.inline_message_id)
        #bot.editMessageReplyMarkup(inline_message_id=update.callback_query.inline_message_id)
    else:
        logger.info("unnecessary clicking")
        pass        
