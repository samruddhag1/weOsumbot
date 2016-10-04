# -*- coding: utf-8 -*-

#using python-telegram-bot modules

import telegram
from telegram.ext import Updater




def askhowMuch(bot , update):
    text = "How much?"
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    print ('asked')
    
    return 'waitingforamount'

def verifyAmount(bot, update):
    str_amt=update.message.text
    print('verify_caught')
    
    try :
        amount = eval(str_amt)
        print (amount)
        text = 'The amount is {}'.format(amount)
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
        return -1
        
    except:
        try_again = "Sorry, could not read a *valid* amount!!\nWhats valid? Try something you would type in a calci.\n"
        try_again+= "You can also type _/cancel_ to abort"
        
        bot.sendMessage(chat_id=update.message.chat_id, text = try_again, parse_mode=telegram.ParseMode.MARKDOWN)
        return 'waitingforamount'
def cancel(bot, update):
    text = 'Ok. Going back to my world.'
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    return -1

def echo(bot ,update):
    bot.sendMessage(chat_id=update.message.chat_id, text = update.message.text+' You!')
        
######Temp for Testing Only######
updater = Updater(token='292385752:AAFCJrNmm_x47FFk_VzJqQFToDnZ7BdQKCU')
dispatcher = updater.dispatcher
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler , Filters

cancel_handler = CommandHandler('cancel',cancel)
iosum_handler = CommandHandler('iosum',askhowMuch)
verifyAmount_handler = MessageHandler([Filters.text ], verifyAmount)
iosumconv_handler = ConversationHandler([iosum_handler],{'waitingforamount': [verifyAmount_handler]},[cancel_handler] )
echo_handler = MessageHandler([Filters.text], echo)

dispatcher.add_handler(iosum_handler)
dispatcher.add_handler(iosumconv_handler)
dispatcher.add_handler(cancel_handler)
dispatcher.add_handler(verifyAmount_handler)
#dispatcher.add_handler(echo_handler)


print('hello')
#################################