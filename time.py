import telebot
import random
import string
import time

active_codes = {}  # Stores codes and their expiry time
user_access = {}  # Stores user access and expiry time

# Function to generate a unique code
def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Admin creates a redeem code
@bot.message_handler(commands=["code"])
def create_code(message):
    if str(message.from_user.id) not in owners:  # Only admin can generate codes
        bot.reply_to(message, "❌ You are not authorized to create codes.")
        return

    args = message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        bot.reply_to(message, "⚠️ Usage: `/code <days>`\nExample: `/code 2` for 2 days", parse_mode="Markdown")
        return

    days = int(args[1])
    expire_time = time.time() + (days * 86400)  # Convert days to seconds
    code = generate_code()

    active_codes[code] = expire_time  # Store code with expiry time

    bot.reply_to(message, f"✅ New Redeem Code:\n`{code}` (Valid for {days} days)", parse_mode="Markdown")

# User redeems a code
@bot.message_handler(commands=["redeem"])
def redeem_code(message):
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Usage: `/redeem <code>`\nExample: `/redeem ABC123XYZ`", parse_mode="Markdown")
        return

    code = args[1]
    current_time = time.time()

    if code not in active_codes:
        bot.reply_to(message, "❌ Invalid Redeem Code.")
        return

    if active_codes[code] < current_time:  # Check expiration
        del active_codes[code]
        bot.reply_to(message, "❌ This code has expired.")
        return

    user_access[message.from_user.id] = active_codes[code]  # Grant access
    del active_codes[code]  # Remove code after use

    bot.reply_to(message, f"✅ Access granted!\nYour access is valid until <b>{time.ctime(user_access[message.from_user.id])}</b>.", parse_mode="HTML")

# User checks their access
@bot.message_handler(commands=["info"])
def check_access(message):
    current_time = time.time()

    if message.from_user.id in user_access:
        if user_access[message.from_user.id] > current_time:
            bot.reply_to(message, f"✅ You have access!\nExpires on: <b>{time.ctime(user_access[message.from_user.id])}</b>", parse_mode="HTML")
            return
        else:
            del user_access[message.from_user.id]  # Remove expired access
            bot.reply_to(message, "❌ Your access has expired.")
            return

    bot.reply_to(message, "❌ You do not have an active subscription.")

bot.polling()
