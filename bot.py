from telebot import TeleBot , types
import query
from dotenv import load_dotenv
import os

import flask
from flask import request

from schema import create_tables

create_tables()

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')


bot =TeleBot(BOT_TOKEN,threaded=False)


app = flask.Flask(__name__)

user_state = {} 
""" Start """
admins = ['6618292400']
@bot.message_handler(['start'])
def start_cdm(message):
    chat_id = message.chat.id
    user_id = str(message.from_user.id)
    user_name = message.from_user.username
    query.insert_user(user_id,user_name)
    
    MarkUp = types.ReplyKeyboardMarkup(resize_keyboard=True)
    MarkUp.row('Available Servises','My Appointments')

    if user_id in admins:
        MarkUp.row('➕Add service')

    bot.send_message(chat_id,f'Welcome to our bot {user_name} \n please choose an option',reply_markup=MarkUp)

""" Service """
@bot.message_handler(func=lambda message : message.text=='Available Servises')
def choose_service(message):
    services = query.get_services()
    markup = types.InlineKeyboardMarkup()
    for sid, name in services:
        markup.add(types.InlineKeyboardButton(name, callback_data=f"service_{sid}"))
    bot.send_message(message.chat.id, "Choose a service:", reply_markup=markup)
""" Date """
@bot.callback_query_handler(func=lambda call:call.data.startswith('service_'))
def choose_date(call):
    service_id = int(call.data.split("_")[1])    
    user_state[call.from_user.id] = {'service_id':service_id}
    dates = query.get_dates(service_id)
    markup = types.InlineKeyboardMarkup()
    for date in dates:
        markup.add(types.InlineKeyboardButton(date,callback_data=f"date_{date}"))
    bot.send_message(call.message.chat.id,'choose your date',reply_markup=markup)
"""  """
@bot.callback_query_handler(func=lambda call:call.data.startswith('date_'))
def choose_time(call):
    date = call.data.split('_')[1]
    user_state[call.from_user.id]['date'] = date
    service_id = user_state[call.from_user.id]['service_id']
    times = query.get_times(service_id,date)
    markup = types.InlineKeyboardMarkup()
    for slot_id,time in times:
        markup.add(types.InlineKeyboardButton(time,callback_data=f"time_{slot_id}"))
    bot.send_message(call.message.chat.id,'choose your time',reply_markup=markup)
""" confirm """
@bot.callback_query_handler(func=lambda call:call.data.startswith('time_'))
def confirm(call):
    user_id = str(call.from_user.id)
    slot_id = int(call.data.split('_')[1])
    query.book_appointments(user_id,slot_id)
    query.update_slots_status(slot_id)
    bot.send_message(call.message.chat.id,'✅ Appoinments books and time reserved')
    user_state.pop(call.from_user.id,None)
""" show appointments """
@bot.message_handler(func=lambda message:message.text=='My Appointments')
def show_appointments(message):
    user_id = str(message.from_user.id)
    chat_id = message.chat.id
    if user_id in admins:
        appointments = query.get_admin_appointments(user_id)
        if not appointments:
            bot.send_message(chat_id,'📭 no appointments have been booked for yor service yet')
            return
        text = "📋 Appointments booked by users:\n\n"
        for date,time,service,username in appointments:
            text+=f"• {service} booked on {date} at {time} - booked by @{username}\n"
        bot.send_message(chat_id,text)
    else:
        appointments=query.get_user_appointments(user_id)
        if not appointments:
            bot.send_message(chat_id,'you have no appointments yet')
            return
        text = "📅 your appointments:\n\n"
        for date,time,service in appointments:
            text+=f"• {service} on {date} at {time}\n"
        bot.send_message(chat_id,text)
""" ServiceName """
@bot.message_handler(func=lambda m:m.text=='➕Add service')
def ask_servic_name(message):
    chat_id = message.chat.id
    admin_id = str(message.from_user.id)
    if admin_id not in admins:
        bot.send_message(chat_id,'❌ you dont have permissionto add service')
    user_state[admin_id]={'step':'service_name','dates':[],'slots':[]}
    bot.send_message(chat_id,'📝 enter your service name:')
""" Handle Admin Input """
@bot.message_handler(func=lambda m:str(m.from_user.id) in user_state)
def handle_admin_input(message):
    chat_id = message.chat.id
    admin_id = str(message.from_user.id)
    admin_stage=user_state[admin_id]
    step = admin_stage['step']
    if step=='service_name':
        admin_stage['service_name']=message.text.strip()
        admin_stage['step']='add_date'
        bot.send_message(chat_id,'📅 Enter a date (YYYY-MM-DD), or type "done" when finished:')
    elif step=='add_date':
        text = message.text.strip()
        if text.lower()=='done':
            if not admin_stage['dates']:
                bot.send_message(chat_id,'⚠️ You must enter at least one date.')
                return
            admin_stage['date_index']=0
            admin_stage['step']='add_time'
            bot.send_message(chat_id,f'⏰ enter time for {admin_stage["dates"][0]} divide with (comma-seperate)')
        else:
            admin_stage['dates'].append(text)
            bot.send_message(chat_id,'✅ date booked successfuly,add another date or type done')
    elif step=='add_time':
        times = [time.strip() for time in message.text.split('_') if time.strip()]
        dates = admin_stage['dates'][admin_stage['date_index']]
        admin_stage['slots'].append((dates,times))
        admin_stage['date_index']+=1
        if admin_stage['date_index'] < len(admin_stage['dates']):
            next_date=admin_stage['dates'][admin_stage['date_index']]
            bot.send_message(chat_id,f'⏰ enter time for {next_date}')
        else:
            service_id = query.insert_service(admin_stage['service_name'],admin_id)
            for date,time in admin_stage['slots']:
                query.insert_slots(service_id,date,time)
            bot.send_message(chat_id,f'✅ Service {admin_stage["service_name"]} wiht {len(admin_stage["dates"])}')
            user_state.pop(admin_id)

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    raw = request.get_data().decode("utf-8")
    print(f"📦 Raw update: {raw}")  # Log the full payload
    update = types.Update.de_json(raw)
    print(f"✅ Parsed update: {update}")  # Log the parsed object
    bot.process_new_updates([update])
    return "OK", 200


@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)