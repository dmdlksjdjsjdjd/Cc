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
