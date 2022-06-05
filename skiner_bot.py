from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import logging
import copy
import cv2, os
import numpy as np
from skin_detection import check_skin
from predict import predict_class
import matplotlib.pyplot as plt

content = {}
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def error(update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def start_handler(update,context):
    chat_id = update.message.chat.username
    update.message.reply_text(f'Welcome {chat_id} to our skin diagnosing chatbot. It would be nice helping you 😊😊')

def help_handler(update,context):
    update.message.reply_text("Please send a picture of the affected area fast. So that we can help you 🙁🙁🙁🙁")

def photo_handler(update,context):
    chat_id = update.message.chat.username
    if update.message.photo != []:
        upd = copy.deepcopy(update.to_dict())
        user_id = update.message.from_user.id
        f_name = update.message.from_user.first_name
        l_name = update.message.from_user.last_name
        #content['user_id'] = user_id
        #if l_name is None:
         #   content['name'] = f_name
        #else:
         #   content['name'] = f_name + ' ' + l_name
        #content['file_info'] = update.message.photo[-1].get_file()#['C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp']
        image = update.message.photo[-1].get_file().download('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp/userpic_' + str(chat_id) + '.jpg')

        #content['file_info'] = update.message.photo[-1].get_file()
        #image = update.message.photo[-1].get_file().download("img.jpg")

        # After Photo ask for location and contact
        location_keyboard = telegram.KeyboardButton(text="send location📍📍", request_location=True)
        contact_keyboard = telegram.KeyboardButton(text="send contact📞📞", request_contact=True)
        custom_keyboard = [[location_keyboard, contact_keyboard]]
        #custom_keyboard = [[location_keyboard]]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        #context.bot.send_message(chat_id=chat_id,text="Would you mind sharing your location and contact with us?",reply_markup=reply_markup)
        update.message.reply_text("Please share your location and mobile number with us 😊😊",reply_markup=reply_markup)
        #update.message.reply_text("Tag the above message☝☝️☝☝️ and share your current location📍📍 by clicking on the pin📎 using telegram and phone number 📞📞 one by one 😊😊")
        #update.message.reply_text("Format of phone number ----> countrycode phonenumber, eg: 181 8543210123")
        #update.message.reply_markup(reply_markup)

def location_handler(update,context):
    upd = copy.deepcopy(update.to_dict())
    if upd.get('message').get('location') is not None:
        location_handler.lat = upd.get('message').get('location').get('latitude')
        location_handler.lng = upd.get('message').get('location').get('longitude')
        # print(str(lat) + ',' + str(lng))
        content['lat'] = str(lat)
        content['long'] = str(lng)
        #update.message.reply_text(f"Your current latitude: {lat} and longitude: {lng}")


def contact_handler(update,context):
    chat_id = update.message.chat.username
    #upd = update.to_dict()
    upd = copy.deepcopy(update.to_dict())
    if upd.get('message').get('contact') is not None:
        phone_no = str('+') + upd.get('message').get('contact').get('phone_number')
        #content['contact'] = phone_no
        #update.message.reply_text(f"Your phone no: {phone_no}")
    
    if check_skin('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp/userpic_' + str(chat_id) + '.jpg'):
            
        preds_dict = predict_class('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp/userpic_' + str(chat_id) + '.jpg')

        dict_dis = sorted(preds_dict.items(), key=lambda x: x[1], reverse=True)
        print(dict_dis)
        dict_dis = dict(sorted(preds_dict.items(), key=lambda x: x[1], reverse=True)[:3])
        max_val = max(dict_dis, key=dict_dis.get)
        if dict_dis[max_val] <= 41:
            update.message.reply_text('Healthy Skin Detected. There is nothing to worry. 😊❤️❤️😊')
            update.message.reply_text("Thank you for reaching to us hope you liked our assistance 😊😊❤️❤️")
        else:
            plt.bar(range(len(dict_dis)), list(dict_dis.values()), align='center')
            x1,x2,y1,y2 = plt.axis()
            plt.axis((x1,x2,0,100))
            plt.xticks(range(len(dict_dis)), range(len(dict_dis)))
            plt.savefig('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp_fig/graph.png')
            #context.bot.send_message(chat_id=update.message.chat_id, text="Thank you!\n \nYou will recieve your report Soon")
            #context.bot.send_photo(chat_id=update.message.chat_id, photo=open('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp/plots/tempfig.png', 'rb'))
            update.message.reply_text("Thank you 😊😊\n \nYou will recieve your report Soon")
            update.message.reply_photo(photo=open('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp_fig/graph.png', 'rb'))
            keys = list(dict_dis.keys())
            #message_text = '0 ->' + str(keys[0]) + '\n1 ->' + str(keys[1]) + '\n2 ->' + str(keys[2]) 
            update.message.reply_text(f' 0 -> {keys[0]}\n \n1 -> {keys[1]}\n \n2 -> {keys[2]}\n')
            update.message.reply_text(f'You have highest possibility of {keys[0]}')
            update.message.reply_text(f'https://www.google.com/maps/search/nearby+dermatalogists+curing+{keys[0].replace(" ","")}/@{location_handler.lat},{location_handler.lng}')
            update.message.reply_text('Please go to the above link provided 👆👆👆 and you may find the best doctors nearby your location 😊😊')
            update.message.reply_text(f'Thank you for taking my help and hoping it was useful 😊😊❤️❤️\n \nGet well soon {chat_id} ❤️❤️')
            os.remove('C:/Users/KIIT/Downloads/NTT AI DATA HACKATHON/Practice/skin dataset/temp/plots/tempfig.png')


            #update.google_place_id(f'Doctors nearby around {lat} and {lng} curing {keys[0]}')
            plt.cla()
            
            #keys = list(dict_dis.keys())
            #message_text = '0 ->' + str(keys[0]) + '\n1 ->' + str(keys[1]) + '\n2 ->' + str(keys[2]) 
            #message_text = '0 ->' + str(keys[0]) + '\n1 ->' + str(keys[1]) + '\n2 ->' + str(keys[2])
            #update.send_message(message_text)
            #update.message.reply_text(f' 0-> {dict_dis[0]}')
    else:
        update.message.reply_text('Please Upload Infected Skin Area for Diagnosis 🙁🙁')

def main():
    update = Updater("5300539005:AAGNv24z2P8ziLXHtfsoCg8V2cHMAbfLZ9g")
    dp = update.dispatcher

    ## Adding Command Handler and Message Handler
    start_cmd_handler = CommandHandler('start', start_handler)
    help_cmd_handler = CommandHandler('help', help_handler)
    photo_msg_handler = MessageHandler(Filters.photo, photo_handler)
    location_msg_handler = MessageHandler(Filters.location, location_handler)
    contact_msg_handler = MessageHandler(Filters.reply, contact_handler)

    dp.add_handler(start_cmd_handler)
    dp.add_handler(help_cmd_handler)
    dp.add_handler(photo_msg_handler)
    dp.add_handler(location_msg_handler)
    dp.add_handler(contact_msg_handler)
    # log all errors
    dp.add_error_handler(error)

    update.start_polling()

    update.idle()



if __name__ == "__main__":
    main()
    content = {}