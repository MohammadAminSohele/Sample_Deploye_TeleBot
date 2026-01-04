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


user_answers = {}


# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Add Question", "Take Quiz", "My Results")

    bot.send_message(message.chat.id, "Welcome to Quiz Bot!", reply_markup=markup)
    


# Handle main menu
@bot.message_handler(func=lambda msg: msg.text in ["Add Question", "Take Quiz", "My Results"])
def menu_handler(message):
    if message.text == "Add Question":
        bot.send_message(message.chat.id, "Send me the question in this format:\nQuestion | Option1 | Option2 | Option3 | Option4 | CorrectOptionNumber")
        bot.register_next_step_handler(message, add_question_handler)
    elif message.text == "Take Quiz":
        start_quiz(message)
    elif message.text == "My Results":
        scores = query.get_user_results(message.from_user.id)
        if scores:
            avg = sum(s[0] for s in scores) / len(scores)
            bot.send_message(message.chat.id, f"Your past scores: {[s[0] for s in scores]}\nAverage: {avg:.2f}")
        else:
            bot.send_message(message.chat.id, "No results found.")

# Add question

def add_question_handler(message):
    try:
        parts = message.text.split("|")
        if len(parts) != 6:
            raise ValueError
        question, o1, o2, o3, o4, correct = [p.strip() for p in parts]
        query.add_question(question, o1, o2, o3, o4, int(correct))
        bot.send_message(message.chat.id, "Question added successfully!")
    except Exception:
        bot.send_message(message.chat.id, "Invalid format. Try again.")

# Quiz handling

def start_quiz(message):
    questions = query.get_all_questions()
    if not questions:
        bot.send_message(message.chat.id, "No questions available.")
        return
    user_answers[message.from_user.id] = {"questions": questions, "current": 0, "score": 0}
    send_question(message.chat.id, message.from_user.id)

'''
user_answers{

            user_id:{
                       'questions': questions,
                       'current':1,
                       'score':1

            
            }






}


'''




def send_question(chat_id, user_id):
    state = user_answers[user_id]
    if state["current"] < len(state["questions"]):
        q = state["questions"][state["current"]]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("1", "2", "3", "4")
        bot.send_message(chat_id, f"Q: {q[1]}\n1) {q[2]}\n2) {q[3]}\n3) {q[4]}\n4) {q[5]}", reply_markup=markup)

        bot.register_next_step_handler_by_chat_id(chat_id, check_answer)
    else:
        finish_quiz(chat_id, user_id)

def check_answer(message):
    user_id = message.from_user.id
    state = user_answers[user_id]
    q = state["questions"][state["current"]]
    try:
        if int(message.text) == q[6]:
            state["score"] += 1
    except:
        pass
    state["current"] += 1
    send_question(message.chat.id, user_id)

def finish_quiz(chat_id, user_id):
    state = user_answers[user_id]
    score = state["score"]
    total = len(state["questions"])
    query.save_result(user_id, score)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Add Question", "Take Quiz", "My Results")

    bot.send_message(chat_id, f"Quiz finished! Your score: {score}/{total}", reply_markup=markup)
    del user_answers[user_id]









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