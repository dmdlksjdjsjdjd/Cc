# Your Handy API Key (replace with your actual key)
API_KEY = "PUB-0YA95V649Pv3wBgjzltHc8WdQ"

# Function to fetch card details from Handy API (or BINlist API)
def fetch_card_info(card_number):
    # Handy API endpoint for BIN lookup (replace this URL if using a different endpoint)
    api_url = f"https://api.bincodeapi.com/v1/lookup/{card_number}"

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    # Make the API request to fetch BIN details
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

# Handler for the /vbv command
@bot.message_handler(commands=["vbv"])
def vbv(message):
    # Ensure there is a card number provided
    if len(message.text.split()) < 2:
        bot.reply_to(message, "Please provide a card number after the command. Example: /vbv 4411037148130658")
        return
    
    card_number = message.text.split()[1]  # Get the card number from the message
    
    # Validate the card number format (13 to 19 digits)
    cleaned_card_number = card_number.replace(" ", "")  # Remove spaces
    if not cleaned_card_number.isdigit() or len(cleaned_card_number) < 13 or len(cleaned_card_number) > 19:
        bot.reply_to(message, "Please enter a valid card number with 13 to 19 digits.")
        return

    bot.reply_to(message, "🔄 Performing VBV lookup... Please wait.")

    start_time = time.time()
    card_info = fetch_card_info(cleaned_card_number)

    if card_info:
        # Extract details from API response
        card_type = card_info.get('type', 'Unknown')
        issuer = card_info.get('bank', {}).get('name', 'Unknown')
        country = card_info.get('country', {}).get('name', 'Unknown')
        gateway = "3DS Lookup"
        
        # Check VBV or 3DS status (Mocked for VBV/3DS)
        vbv_status = card_info.get('3ds_status', 'Unknown')  # Example field; adjust as needed
        if vbv_status == "passed":
            response = "3DS Authenticate Successful"
            # Passed format
            message_text = f"""
𝗣𝗮𝘀𝘀𝗲𝗱 ✅

𝗖𝗮𝗿𝗱 ⇾ {card_number}
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ {gateway}
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⇾ {response}

𝗜𝗻𝗳𝗼 ⇾ {card_type}
𝐈𝐬𝐬𝐮𝐞𝐫 ⇾ {issuer}
𝐂𝐨𝐮𝐧𝐭𝐫𝘆 ⇾ {country}

𝗧𝗶𝗺𝗲 ⇾ {round(time.time() - start_time, 2)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
            """
        else:
            # Rejected format
            response = "3DS Authentication Failed or Rejected"
            message_text = f"""
❌️ VBV REJECTED

𝗖𝗮𝗿𝗱 ⇾ {card_number}
𝐆𝐚𝐭𝐞𝐰𝐚𝐲 ⇾ {gateway}
𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞 ⇾ {response}

𝗜𝗻𝗳𝗼 ⇾ {card_type}
𝐈𝐬𝐬𝐮𝐞𝐫 ⇾ {issuer}
𝐂𝐨𝐮𝐧𝐭𝐫𝘆 ⇾ {country}

𝗧𝗶𝗺𝗲 ⇾ {round(time.time() - start_time, 2)} 𝘀𝗲𝗰𝗼𝗻𝗱𝘀
            """
        
        bot.reply_to(message, message_text)
    else:
        bot.reply_to(message, "❌ Card details not found. Please try again with a valid card number.")