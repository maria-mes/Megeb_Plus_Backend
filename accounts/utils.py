import os
import random
import string
import requests


def generate_otp(length=6):
    return "".join(random.choice(string.digits) for _ in range(length))


def send_sms(phone, message):
    token = os.getenv("AFROMESSAGE_TOKEN")
    identifier_id = os.getenv("AFROMESSAGE_IDENTIFIER_ID")

    if token and identifier_id:
        url = "https://api.afromessage.com/api/send"
        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "from": identifier_id,
            "to": phone,
            "message": message,
        }

        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            if data.get("acknowledge") == "success":
                print(f"[AfroMessage] sent to {phone}")
                return True
            else:
                print(f"[AfroMessage] failed: {data}")
        except Exception as exc:
            print(f"[AfroMessage] error: {exc}")

    print(f"[AfroMessage] mocked SMS to {phone}: {message}")
    return True