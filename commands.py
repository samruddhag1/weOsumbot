# -*- coding: utf-8 -*-

#using python-telegram-bot modules

import telegram
from telegram.ext import Updater

#States 
VERIFYAMOUNT,VERIFYPERSON = range(2)
END = -1


def askAmount(bot , update):
    text = "How much?"
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    print ('asked amount')
    
    return VERIFYAMOUNT
def askPerson(bot, update):
    text = "Who's e (he/she/whatever)?"
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    print ('asked person')
    
def verifyAmount(bot, update):
    str_amt=update.message.text
    print('verify_caught')
    
    try :
        amount = eval(str_amt)
        print (amount)
        text = 'The amount is {}'.format(amount)
        bot.sendMessage(chat_id=update.message.chat_id, text=text)
        
        askPerson(bot, update)
        return VERIFYPERSON
        
    except:
        try_again = "Sorry, could not read a *valid* amount!!\nWhats valid? Try something you would type in a calci.\n"
        try_again+= "You can also type _/cancel_ to abort"
        
        bot.sendMessage(chat_id=update.message.chat_id, text = try_again, parse_mode=telegram.ParseMode.MARKDOWN)
        return VERIFYAMOUNT
    pass

#def verifyPerson(bot, update):
    

def cancel(bot, update):
    text = 'Ok. Going back to my world.'
    bot.sendMessage(chat_id=update.message.chat_id, text=text)
    return -1

def echo(bot ,update):
    bot.sendMessage(chat_id=update.message.chat_id, text = update.message.text+' You!')

def askContact(bot,update):
     contact_keyboard = telegram.KeyboardButton(text="send_contact", request_contact=True)
     custom_keyboard = [[ contact_keyboard ]]
     reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
     bot.sendMessage(chat_id=update.message.chat_id, text="Would mind to share location and contact with me ?",reply_markup=reply_markup) 
        
######Temp for Testing Only######
updater = Updater(token='292385752:AAFCJrNmm_x47FFk_VzJqQFToDnZ7BdQKCU')
dispatcher = updater.dispatcher
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import MessageHandler , Filters

cancel_handler = CommandHandler('cancel',cancel)
iosum_handler = CommandHandler('iosum',askAmount)
verifyAmount_handler = MessageHandler([Filters.text ], verifyAmount)
iosumconv_handler = ConversationHandler([iosum_handler],{VERIFYAMOUNT: [verifyAmount_handler]},[cancel_handler] )
echo_handler = MessageHandler([Filters.text], echo)
contact_handler = CommandHandler('contact',askContact)
#.add_handler(iosum_handler)
dispatcher.add_handler(iosumconv_handler)
dispatcher.add_handler(contact_handler)
#dispatcher.add_handler(cancel_handler)
#dispatcher.add_handler(verifyAmount_handler)
#dispatcher.add_handler(echo_handler)
updater.start_polling()
#updater.idle()

#updater.stop()
print('Bye')
#################################
