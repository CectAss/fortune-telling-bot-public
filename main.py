#------------------------------------------------------------------------ Комменты и код полностью написаны мной (Cectus4), по вопросам тг: @cectus1 -----------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------- Имопрт библиотек и конфига------------------------------------------------------------------------------------------------

import telebot
from config import *
from datetime import datetime
from random import choice
import threading
from telebot import types

#---------------------------------------------------------------------------------------------- Инициальзация бота ----------------------------------------------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)                                                                    # Подключение к апи телеграма

#---------------------------------------------------------------------------------------------- Создание локальных переменных и чтение из файла ----------------------------------------------------------------------------------------------

with open(ANSWERS_FILE_NAME, encoding="utf-8") as file:
    
    answers = file.read().split("\n")


with open(FORTUNE_TELLING_FILE_NAME, encoding="utf-8") as file:
    
    fortune_telling = file.read().split("\n")


user_limit = []
fortune_telling_day = datetime.now().day
mailing_day = datetime.now().day
mailing_users = []
mailed_users = []

#---------------------------------------------------------------------------------------------- Функции ----------------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=["start"])
def greeting(message):
    
    bot.send_message(message.chat.id, GREETING_TEXT, 
        reply_markup=keyboard(buttons(message)))



@bot.message_handler()
def on_message(message):

    #print(message.text, message.chat.id, datetime.now())

    if(message.text in [MAIN_BUTTONS.get("fortune_telling"), FORTUNE_TELLING_BUTTONS[0]]):    # Гадание

        fortune_telling_say(message) # Вызов функции fortune_telling_say


    elif(message.text==MAIN_BUTTONS.get("ask_a_question")):    # Вопрос

        bot.send_message(message.chat.id, choice(QUESTION_TEXT), 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))
        bot.register_next_step_handler(message, question)


    elif(message.text==MAIN_BUTTONS.get("mailing")):    # Подключение рассылки

        horoscope_subscribe(message)
    

    elif(message.text==MAIN_BUTTONS.get("info")): # Инфа

        bot.send_message(message.chat.id, INFO_TEXT,                                                        
            reply_markup=keyboard(dict_to_arr(INFO_BUTTONS)+[DISTRIBUTION_BUTTON]))
        bot.register_next_step_handler(message, info)
    

    else:
 
        if(str(message.chat.id) in ALLOWED_USERS and
           message.text==ADMIN_BUTTON):    # Админка
            bot.send_message(message.chat.id, ADMIN_TEXT,                                                        
                reply_markup=keyboard(dict_to_arr(ADMIN_BUTTONS)+[DISTRIBUTION_BUTTON]))
            bot.register_next_step_handler(message, admin_buttons)
        

        else:

            bot.send_message(message.chat.id, MAIN_TEXT,        
                reply_markup=keyboard(buttons(message)))



def admin_buttons(message):

    global user_limit

    if(message.text==DISTRIBUTION_BUTTON):                                                          
        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))   

    elif(message.text==ADMIN_BUTTONS.get("mailing_test")):
                
        for id in mailing_users:

            bot.send_message(id, mail)

        bot.send_message(message.chat.id, SUCCESS_TEXT, 
            reply_markup=keyboard(buttons(message)))
            
    
    elif(message.text==ADMIN_BUTTONS.get("drop_limit")):

        user_limit.clear()
        bot.send_message(message.chat.id, SUCCESS_TEXT, 
            reply_markup=keyboard(buttons(message)))


    elif(message.text==ADMIN_BUTTONS.get("set_fortune_telling")):

        bot.send_message(message.chat.id, SET_FILE_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))
        bot.register_next_step_handler(message, set_fortune_telling)


    elif(message.text==ADMIN_BUTTONS.get("get_fortune_telling")):

        bot.send_document(message.chat.id, open(FORTUNE_TELLING_FILE_NAME, 'rb'), 
            reply_markup=keyboard(buttons(message)))
    
            
    elif(message.text==ADMIN_BUTTONS.get("set_answers")):

        bot.send_message(message.chat.id, SET_FILE_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))
        bot.register_next_step_handler(message, set_answers)


    elif(message.text==ADMIN_BUTTONS.get("get_answers")):

        bot.send_document(message.chat.id, open(ANSWERS_FILE_NAME, 'rb'), 
            reply_markup=keyboard(buttons(message)))



def question(message):                                                                              

    if(message.text==DISTRIBUTION_BUTTON):                                                         
        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))                                      


    else:     

        bot.send_message(message.chat.id, choice(answers), 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))                                                                                  



def horoscope_subscribe(message):
    
    if(str(message.chat.id) in mailing_users):

        bot.send_message(message.chat.id, choice(MAILING_TEXT),
            reply_markup=keyboard([MAILING_BUTTONS.get("unsubscribe")]+[DISTRIBUTION_BUTTON]))
    

    else:
        bot.send_message(message.chat.id, choice(MAILING_TEXT), 
            reply_markup=keyboard([MAILING_BUTTONS.get("subscribe")]+[DISTRIBUTION_BUTTON]))
        

    bot.register_next_step_handler(message, mailing)



def mailing(message):   

    if(message.text==DISTRIBUTION_BUTTON):                                                          
        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))                                                                                         


    elif(message.text==MAILING_BUTTONS.get("subscribe")):           

        bot.send_message(message.chat.id, MAILING_STАRT_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))
        mailing_users.append(str(message.chat.id))


    elif(message.text==MAILING_BUTTONS.get("unsubscribe")):                                                           
        bot.send_message(message.chat.id, MAILING_END_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))                                     
        mailing_users.remove(str(message.chat.id))                                                    


    else:       
           
        bot.send_message(message.chat.id, PRESS_BUTTON_TEXT)
        bot.register_next_step_handler(message, mailing)



def fortune_telling_say(message):
    
    global fortune_telling_day
    global user_limit

    if(datetime.now().day!=fortune_telling_day):

        user_limit.clear()
        fortune_telling_day = datetime.now().day
    

    if(user_limit.count(str(message.chat.id))<DAY_LIMIT):

        bot.send_message(message.chat.id, gen_a_lot_from_arr(fortune_telling, 2), 
            reply_markup=keyboard(FORTUNE_TELLING_BUTTONS+[DISTRIBUTION_BUTTON]))
        user_limit.append(str(message.chat.id))
    

    else:

        bot.send_message(message.chat.id, FORTUNE_TELLING_LIMIT_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))



def info(message):                                                                                                                                        
    
    if(message.text==DISTRIBUTION_BUTTON):

        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))


    elif(message.text==INFO_BUTTONS.get("crew")):

        bot.send_message(message.chat.id, INFO_CREW_TEXT, 
            reply_markup=keyboard(dict_to_arr(INFO_CREW_BUTTONS)+[DISTRIBUTION_BUTTON]))
        bot.register_next_step_handler(message, info_crew)


    elif(message.text==INFO_BUTTONS.get("band")):

        bot.send_message(message.chat.id, INFO_BAND_TEXT, 
                         reply_markup=keyboard(dict_to_arr(INFO_BAND_BUTTONS)+[DISTRIBUTION_BUTTON]))
        bot.register_next_step_handler(message, info_band)


    else:

        bot.send_message(message.chat.id, PRESS_BUTTON_TEXT)
        bot.register_next_step_handler(message, info)



def info_crew(message):

    if(message.text==DISTRIBUTION_BUTTON):

        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))
    

    elif(message.text==INFO_CREW_BUTTONS.get("about")):

        bot.send_message(message.chat.id, INFO_CREW_CONTACT_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))


    elif(message.text==INFO_CREW_BUTTONS.get("photo")):

        bot.send_message(message.chat.id, INFO_CREW_PHOTO_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))


    elif(message.text==INFO_CREW_BUTTONS.get("help")):
        bot.send_message(message.chat.id, INFO_CREW_HELP_TEXT,
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))


    else:

        bot.send_message(message.chat.id, PRESS_BUTTON_TEXT)
        bot.register_next_step_handler(message, info_crew)



def info_band(message):

    if(message.text==DISTRIBUTION_BUTTON):

        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))


    elif(message.text==INFO_BAND_BUTTONS.get("links")):

        bot.send_message(message.chat.id, INFO_BAND_LINK_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))
        

    elif(message.text==INFO_BAND_BUTTONS.get("events")):

        bot.send_message(message.chat.id, INFO_BAND_EVENTS_TEXT, 
            reply_markup=keyboard([DISTRIBUTION_BUTTON]))
        

    else:
        bot.send_message(message.chat.id, PRESS_BUTTON_TEXT)
        bot.register_next_step_handler(message, info_band)



def set_answers(message):

    global answers

    if(message.text==DISTRIBUTION_BUTTON):

        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))


    elif(message.document):                                                             # Дефолтная скачка файла ботом с телеграма мне лень объяснять (если сам захочешь сделать че то такое то просто скопируй эти строчки и поменяй название файла на нужный тебе)
        file_info = bot.get_file(message.document.file_id) 
        downloaded_file = bot.download_file(file_info.file_path)
        with open(ANSWERS_FILE_NAME, 'wb') as file:
            file.write(downloaded_file)
        answers = rewrite(ANSWERS_FILE_NAME)
        bot.send_message(message.chat.id, SUCCESS_TEXT, 
            reply_markup=keyboard(buttons(message)))                                 


    else:

        bot.send_message(message.chat.id, PRESS_BUTTON_TEXT)
        bot.register_next_step_handler(message, set_answers)



def set_fortune_telling(message):

    global fortune_telling

    if(message.text==DISTRIBUTION_BUTTON):

        bot.send_message(message.chat.id, MAIN_TEXT, 
            reply_markup=keyboard(buttons(message)))


    elif(message.document):
        file_info = bot.get_file(message.document.file_id) 
        downloaded_file = bot.download_file(file_info.file_path)
        with open(FORTUNE_TELLING_FILE_NAME, 'wb') as file:
            file.write(downloaded_file)
        fortune_telling = rewrite(FORTUNE_TELLING_FILE_NAME)
        bot.send_message(message.chat.id, SUCCESS_TEXT, 
            reply_markup=keyboard(buttons(message)))                                 


    else:

        bot.send_message(message.chat.id, PRESS_BUTTON_TEXT)
        bot.register_next_step_handler(message, set_fortune_telling)



def check_mailing():

    global mailing_day
    global mailed_users
    global mail


    while True:

        if(datetime.now().day!=mailing_day):

            mailing_day=datetime.now().day
            mailed_users.clear()
            mail=gen_mailing_text()


        for id in mailing_users:

            if not(id in mailed_users):

                bot.send_message(id, mail)
                mailed_users.append(id)


            
def gen_mailing_text():

    return HOROSCOPE_TEXT.format(a=gen_a_lot_from_arr(fortune_telling, 6),
                                 b=gen_a_lot_from_arr(fortune_telling, 6),
                                 c=gen_a_lot_from_arr(fortune_telling, 6),
                                 d=gen_a_lot_from_arr(fortune_telling, 6),
                                 e=gen_a_lot_from_arr(fortune_telling, 6),
                                 f=gen_a_lot_from_arr(fortune_telling, 6),
                                 g=gen_a_lot_from_arr(fortune_telling, 6),
                                 h=gen_a_lot_from_arr(fortune_telling, 6),
                                 i=gen_a_lot_from_arr(fortune_telling, 6),
                                 j=gen_a_lot_from_arr(fortune_telling, 6),
                                 k=gen_a_lot_from_arr(fortune_telling, 6),
                                 l=gen_a_lot_from_arr(fortune_telling, 6))



def gen_a_lot_from_arr(arr, n):

    return ''.join([choice(arr)+" " for i in range(n)])




mail = gen_mailing_text()



def keyboard(button=[]):

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    
    for i in range(len(button)):

        markup.add(types.KeyboardButton(button[i]))


    return markup



def buttons(message):

    if(str(message.chat.id) in ALLOWED_USERS):

        return dict_to_arr(MAIN_BUTTONS)+[ADMIN_BUTTON]
    

    return dict_to_arr(MAIN_BUTTONS)



def rewrite(file_name):

    arr = []

    with open(file_name, encoding="utf-8") as file:
    
        arr = file.read().split("\n")


    return arr




def dict_to_arr(dict):

    return [dict.get(i) for i in dict]



thread = threading.Thread(target=check_mailing)
thread.start()
bot.infinity_polling()