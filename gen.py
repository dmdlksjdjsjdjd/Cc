import random

def luhn_checksum(card_number):
    """Calculate the Luhn checksum of a card number."""
    digits = [int(d) for d in card_number]
    for i in range(len(digits) - 2, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    return sum(digits) % 10

def generate_credit_card(bin_format, quantity=10):
    """Generate valid credit card numbers using a given BIN format."""
    cards = []
    
    for _ in range(quantity):
        card_number = bin_format + ''.join(str(random.randint(0, 9)) for _ in range(15 - len(bin_format)))
        checksum = (10 - luhn_checksum(card_number)) % 10
        card_number += str(checksum)
        cards.append(card_number)

    result = "\n".join(cards)

    if quantity > 10:
        with open("gen.txt", "w") as file:
            file.write(result)
        return "gen.txt"  # Return file path for Dakar.py to use
    
    return result  # Return string output for direct reply

import requests  # If using an API

def get_bin_info(bin_number):
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        response = requests.get(url, headers={"Accept-Version": "3"})
        
        if response.status_code != 200:
            return None

        data = response.json()
        return {
            "bin": bin_number,
            "bank": data.get("bank", {}).get("name", "Unknown"),
            "country": data.get("country", {}).get("name", "Unknown"),
            "country_code": data.get("country", {}).get("alpha2", "N/A"),
            "type": data.get("type", "N/A"),
            "level": data.get("brand", "N/A"),
            "brand": data.get("scheme", "N/A"),
        }
    except Exception:
        return None
