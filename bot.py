import telebot
import requests
import json
import time
import threading
import sqlite3
import random
import string
import html
import os
from html import escape  
from telebot import types
from datetime import datetime, timedelta
from gateo import Tele

TOKEN = "7236086225:9e2npgsq9CDu_jRBwk"
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

DB_FILE = "user.db"
OWNER_ID = 573859211
GROUP_ID = -100237961321
MAX_CARDS = 200

PLANS = {
    "Gold": {"days": 30, "price": 6},
    "Silver": {"days": 15, "price": 4},
    "Bronze": {"days": 5, "price": 2},
    "Custom": {"days": 1, "price": None}
}

processing = {}
stop_processing = {}

if not os.path.exists("redeem_codes.json"):
    with open("redeem_codes.json", "w") as file:
        json.dump([], file)

def load_redeem_codes():
    try:
        with open("redeem_codes.json", "r") as file:
            return json.load(file)
            
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_redeem_codes(codes):
    with open("redeem_codes.json", "w") as file:
        json.dump(codes, file, indent=4)
        
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY, 
                        username TEXT, 
                        subscription TEXT DEFAULT NULL)''')
    conn.commit()
    conn.close()

init_db()

def is_registered(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return bool(user)

def register_user(user_id, username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def is_subscribed(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT subscription FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result and result[0]:
        expiry = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        return expiry > datetime.now()
    return False

def add_subscription(user_id, days):
    expiry = datetime.now() + timedelta(days=days)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET subscription=? WHERE user_id=?", (expiry.strftime("%Y-%m-%d %H:%M:%S"), user_id))
    conn.commit()
    conn.close()
             
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"

    photos = bot.get_user_profile_photos(user_id)
    photo_id = photos.photos[0][-1].file_id if photos.total_count > 0 else None

    markup = types.InlineKeyboardMarkup()
    register_btn = types.InlineKeyboardButton("ᏒᏋᎶᎥᏕᏖᏋᏒ 💎", callback_data="register")
    markup.add(register_btn)

    welcome_text = f"""
♻️ 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 <b>{username}</b> 🌷 •\n
♻️ 𝐔𝐫 𝐈𝐝 <code>{user_id}</code> 👀 •\n
♻️ 𝐔𝐬𝐞 /cmds 𝐅𝐨𝐫 𝐃𝐞𝐭𝐚𝐢𝐥𝐬 🙂 •\n
♻️ 𝐒𝐞𝐧𝐝 𝐓𝐱𝐓 𝐅𝐢𝐥𝐞 𝐓𝐨 𝐜𝐡𝐞𝐜𝐤 𝐜𝐜.𝐭𝐱𝐭 ⌛•\n \n

🚀 𝗥𝗲𝗴𝗶𝘀𝘁𝗲𝗿 𝘁𝗼 𝗮𝗰𝗰𝗲𝘀𝘀 𝗮𝗹𝗹 𝗯𝗼𝘁 𝗳𝗲𝗮𝘁𝘂𝗿𝗲𝘀!
    """
    if photo_id:
        bot.send_photo(user_id, photo_id, caption=welcome_text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(user_id, welcome_text, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == "register")
def register(call):
    user_id = call.from_user.id
    username = call.from_user.username or "Unknown"

    if is_registered(user_id):
        bot.answer_callback_query(call.id, "✅ You are already registered!")
    else:
        register_user(user_id, username)
        bot.answer_callback_query(call.id, "✅ Registration successful!")
        bot.send_message(user_id, "🎉 You are now registered! Use commands freely.")

@bot.message_handler(commands=["plan"])
def show_plans(message):
    plans_text = (
        "📌 <b>Available Plans:</b>\n\n"
        "🥇 <b>Gold </b> – 30 days ($26)\n"
        "🥈 <b>Silver</b> – 15 days ($19)\n"
        "🥉 <b>Bronze</b> – 7 days ($10)\n"
        "⏳ <b>One Day</b> – 1 day ($3)\n\n"
        "📩 Contact @dmifyouwantbot to buy a plan!"
    )

    bot.reply_to(message, plans_text, parse_mode="HTML")
    
@bot.message_handler(commands=["gen"])
def generate_redeem_code(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "Shut Up Niggaa 🤬")
        return

    args = message.text.split()
    if len(args) < 3:
        bot.reply_to(message, "⚠️ Usage: /gen <b>Plan</b> <b>Days</b>", parse_mode="HTML")
        return

    plan_name = args[1].capitalize()
    try:
        days = int(args[2])
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid number of days. Please enter a valid number.")
        return

    def generate_code():
        return f"𝐁𝐑𝐈𝐂𝐇𝐊-{''.join(random.choices(string.ascii_uppercase + string.digits, k=3))}-" \
               f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=3))}-" \
               f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=2))}-" \
               f"{''.join(random.choices(string.ascii_uppercase + string.digits, k=3))}"

    new_code = generate_code()

    codes = load_redeem_codes()

    codes.append({"code": new_code, "days": days, "plan": plan_name})
    save_redeem_codes(codes)

    bot.reply_to(message, 
        f"✅ New redeem code generated!\n\n"
        f"🔑 Code: <code>{new_code}</code>\n"
        f"📅 Validity: {days} days\n"
        f"📦 Plan: <b>{plan_name}</b>", 
        parse_mode="HTML"
    )
    
@bot.message_handler(commands=["id"])
def user_info(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    profile_link = f"<a href='tg://user?id={user_id}'>{username}</a>"

    if not is_registered(user_id):
        bot.reply_to(message, "⚠️ You need to register first using /start.")
        return

    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT subscription FROM users WHERE user_id=?", (user_id,))
        result = cursor.fetchone()
        conn.close()

        print(f"Database Query Result: {result}")

        if result and result[0]:
            expiry_date = datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")

            remaining_days = (expiry_date - datetime.now()).days
            plan_name = "Unknown"

            for plan, details in PLANS.items():
                if details["days"] == remaining_days:
                    plan_name = plan
                    break

            status = "✅ Active" if expiry_date > datetime.now() else "❌ Expired"
        else:
            expiry_date = "N/A"
            plan_name = "No Plan"
            status = "❌ No Plan"

        info_text = f"""
🔍 <b>User Info:</b>

👤 <b>Username:</b> {profile_link} 
🆔 <b>User ID:</b> <code>{user_id}</code>

📦 <b>Plan:</b> {plan_name} 
📆 <b>Status:</b> {status} 
⏳ <b>Expiry Date:</b> {expiry_date if expiry_date != "N/A" else "N/A"} 
"""
        bot.send_message(message.chat.id, info_text, parse_mode="HTML")

    except Exception as e:
        bot.reply_to(message, f"⚠️ An error occurred: {str(e)}")
    
@bot.message_handler(commands=["redeem"])
def redeem_code(message):
    user_id = message.from_user.id
    if not is_registered(user_id):
        bot.reply_to(message, "⚠️ You need to register first using /start.")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Usage: /redeem <Redeem Code>")
        return

    redeem_code = args[1]

    codes = load_redeem_codes()
    for code_entry in codes:
        if code_entry["code"] == redeem_code:
            days = code_entry["days"]
            codes.remove(code_entry)
            save_redeem_codes(codes)  
            
            add_subscription(user_id, days)
            bot.reply_to(message, f"🎉 Congratulations! Your <b>{days}-day plan</b> is activated!\nThanks To @SOULCRACK ✅", parse_mode="HTML")
            return

    bot.reply_to(message, "❌ Invalid redeem code.")
    
@bot.message_handler(commands=["cmds"])
def show_commands(message):
    cmds_message = """
Here’s a quick overview of available commands:

[⌁]  /redeem ⌁ 𝗥𝗲𝗱𝗲𝗲𝗺 𝗮 𝗽𝗹𝗮𝗻
[⌁]  /start ⌁ 𝗦𝘁𝗮𝗿𝘁 𝗧𝗵𝗲 𝗕𝗼𝘁 
[⌁]  /id ⌁ 𝗩𝗶𝗲𝘄 𝘆𝗼𝘂𝗿 𝗽𝗿𝗼𝗳𝗶𝗹𝗲 𝗮𝗻𝗱 𝗰𝗿𝗲𝗱𝗶𝘁𝘀
[⌁]  /plan ⌁ 𝗣𝘂𝗿𝗰𝗵𝗮𝘀𝗲 𝗣𝗹𝗮𝗻 & 𝗗𝗲𝘁𝗮𝗶𝗹𝘀

"""
    bot.reply_to(message, cmds_message)    

@bot.message_handler(commands=["redeem"])
def redeem_code(message):
    user_id = message.from_user.id
    if not is_registered(user_id):
        bot.reply_to(message, "⚠️ You need to register first using /start.")
        return

    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Usage: /redeem <Redeem Code>")
        return

    redeem_code = args[1]

    codes = load_redeem_codes()
    for code_entry in codes:
        if code_entry["code"] == redeem_code:
            days = code_entry["days"]
            codes.remove(code_entry)
            save_redeem_codes(codes)
            
            add_subscription(user_id, days)
            bot.reply_to(message, f"🎉 Congratulations! Your <b>{days}-day plan</b> is activated!\n Thanks To @SOULCRACK ✅", parse_mode="HTML")
            return

    bot.reply_to(message, "❌ Invalid redeem code.")

@bot.message_handler(func=lambda message: True)
def restrict_access(message):
    if not is_registered(message.from_user.id):
        bot.reply_to(message, "⚠️ You need to register first using /start.")
        return

    bot.reply_to(message, " You are registered! ✅ \nUse /plan to check plans.")       
                                                  
@bot.message_handler(content_types=["document"])
def main(message):
    if not is_subscribed(message.from_user.id):
        bot.reply_to(message, "⚠️ <b>You need to buy a plan to check cards.</b>\nUse /plan for details.", parse_mode="HTML")
        return

    user_max_cards = MAX_CARDS if message.from_user.id != OWNER_ID else float('inf')

    if processing.get(message.from_user.id, False):
        bot.reply_to(message, "⚠️ <b>You already have an ongoing check. Please wait.</b>", parse_mode="HTML")
        return

    processing[message.from_user.id] = True
    stop_processing[message.from_user.id] = False

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    file_path = f"combo_{message.from_user.id}.txt"
    with open(file_path, "wb") as w:
        w.write(downloaded_file)

    with open(file_path, 'r') as file:
        total_cards = len(file.readlines())

    if total_cards > user_max_cards:
        bot.reply_to(message, f"<b>Maximum {user_max_cards} cards allowed ⚠️ </b>", parse_mode="HTML")
        processing[message.from_user.id] = False
        return

    ko = bot.send_message(message.chat.id, "<b>𝐖𝐀𝐈𝐓 𝐂𝐇𝐄𝐂𝐊𝐈𝐍𝐆 𝐘𝐎𝐔𝐑 𝐂𝐀𝐑𝐃𝐒...</b> ⌛ ", parse_mode="HTML").message_id

    threading.Thread(target=process_cards, args=(message, ko, file_path)).start()    
def process_cards(message, ko, file_path):
    live, ch, dd = 0, 0, 0
    total_checked = 0

    user = message.from_user
    username = user.username if user.username else f"{user.first_name} {user.last_name if user.last_name else ''}"

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            total = len(lines)

            for cc in lines:
                if stop_processing.get(message.from_user.id, False):
                    bot.send_message(message.chat.id, " <b>Processing stopped 🛑</b>", parse_mode="HTML")
                    break

                cc = cc.strip()
                total_checked += 1

                try:
                    bin_data_url = f"https://bins.antipublic.cc/bins/{cc[:6]}"
                    bin_data = requests.get(bin_data_url).json()
                    brand = bin_data.get('brand', 'Unknown')
                    card_type = bin_data.get('type', 'Unknown')
                    level = bin_data.get('level', 'Unknown')
                    country = bin_data.get('country_name', 'Unknown')
                    country_flag = bin_data.get('country_flag', '')
                    bank = bin_data.get('bank', 'Unknown')
                except Exception as e:
                    brand, card_type, level, country, country_flag, bank = 'Unknown', 'Unknown', 'Unknown', 'Unknown', '', 'Unknown'

                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                cm2 = types.InlineKeyboardButton(f"• Live ✅: [ {ch} ] •", callback_data='x')
                cm3 = types.InlineKeyboardButton(f"• Risk ⚠️ : [ {live} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"• Dead ❌ : [ {dd} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"• Total 💎 : [ {total_checked} / {total} ] •", callback_data='x')
                stop_btn = types.InlineKeyboardButton("[ Stop 🛑 ] ", callback_data='stop_process')
                mes.add(cm1, cm2, cm3, cm4, cm5, stop_btn)

                try:
                    bot.edit_message_text(
                        chat_id=message.chat.id,
                        message_id=ko,
                        text="𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝘾𝘼𝙍𝘿𝙎...🧊\nGate- Braintree Auth 💎",
                        reply_markup=mes
                    )
                except telebot.apihelper.ApiTelegramException as e:
                    if "message is not modified" not in str(e):
                        print(f"Edit Message Error: {e}")

                try:
                    last = str(Tele(cc))
                except Exception as e:
                    print(e)
                    last = "Your card was declined."

                msg = f'''𝘋𝘦𝘤𝘭𝘪𝘯𝘦𝘥 ❌

💳 𝘊𝘢𝘳𝘥: {cc}
💎 𝘙𝘦𝘴𝘶𝘭𝘵: ⤿ Payment Method Added Successfully ⤾ 

🔍 𝘉𝘪𝘯: {card_type} - {brand} - {level}
🏦 𝘉𝘢𝘯𝘬: {bank}
🌏 𝘊𝘰𝘶𝘯𝘵𝘳𝘺: {country} {country_flag}
🛡️ 𝘗𝘳𝘰𝘹𝘺: Proxy Live ✅

🔍 𝘊𝘩𝘦𝘤𝘬𝘦𝘥 𝘉𝘺: @{username} 
👀 𝘉𝘰𝘵 𝘣𝘺: {OWNER_ID} 
'''

                if "requires_action" in last or "Your card does not support this type of purchase." in last or \
                   "Your card's security code is incorrect." in last or "Your card's security code is invalid." in last or "Your card has insufficient funds." in last :
                    live += 1
                elif "succeeded" in last:
                    ch += 1                
                    msg1 = f'''𝘈𝘱𝘱𝘳𝘰𝘷𝘦𝘥 ✅

💳 𝘊𝘢𝘳𝘥: {cc}
💎 𝘙𝘦𝘴𝘶𝘭𝘵: ⤿ Payment Method Added Successfully ⤾

🔍 𝘉𝘪𝘯: {card_type} - {brand} - {level}
🏦 𝘉𝘢𝘯𝘬: {bank}
🌏 𝘊𝘰𝘶𝘯𝘵𝘳𝘺: {country} {country_flag}
🛡️ 𝘗𝘳𝘰𝘹𝘺: Proxy Live ✅

🔍 𝘊𝘩𝘦𝘤𝘬𝘦𝘥 𝘉𝘺: @{username} 
👀 𝘉𝘰𝘵 𝘣𝘺: @dmifyouwantbot
'''

                    bot.send_message(GROUP_ID, msg1)
                    bot.send_message(message.chat.id, msg1)
                else:
                    dd += 1

    finally:
        processing[message.from_user.id] = False
        stop_processing[message.from_user.id] = False

@bot.callback_query_handler(func=lambda call: call.data == 'stop_process')
def stop_processing_callback(call):
    bot.answer_callback_query(call.id)
    stop_processing[call.from_user.id] = True
    bot.send_message(call.message.chat.id, " <b>Processing Your Request ⌛</b>", parse_mode="HTML") 
              

bot.polling(none_stop=True)