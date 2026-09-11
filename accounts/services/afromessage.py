
import requests
from django.conf import settings


def _parse_afromessage_response(response, operation):
    """
    Safely parse an AfroMessage response.

    Prevents JSONDecodeError when AfroMessage returns:
    - an empty response
    - HTML/text instead of JSON
    - a non-2xx response
    """

    print(
        f"AFROMESSAGE {operation} STATUS:",
        response.status_code
    )

    print(
        f"AFROMESSAGE {operation} CONTENT-TYPE:",
        response.headers.get("Content-Type")
    )

    print(
        f"AFROMESSAGE {operation} RESPONSE:",
        response.text
    )

    # --------------------------------------------------------
    # HTTP error
    # --------------------------------------------------------

    if not response.ok:
        return {
            "acknowledge": "error",
            "response": {
                "errors": [
                    (
                        f"AfroMessage HTTP "
                        f"{response.status_code}: "
                        f"{response.text[:500]}"
                    )
                ]
            }
        }

    # --------------------------------------------------------
    # Try JSON
    # --------------------------------------------------------

    try:
        return response.json()

    except ValueError as e:
        return {
            "acknowledge": "error",
            "response": {
                "errors": [
                    (
                        "AfroMessage returned invalid JSON: "
                        f"{str(e)}"
                    ),
                    (
                        "Raw response: "
                        f"{response.text[:500]}"
                    )
                ]
            }
        }


# ============================================================
# SEND OTP
# ============================================================

def send_otp(phone):

    url = "https://api.afromessage.com/api/challenge"

    headers = {
        "Authorization": (
            f"Bearer {settings.AFROMESSAGE_TOKEN}"
        ),
        "Accept": "application/json",
    }

    params = {
        "from": settings.AFROMESSAGE_IDENTIFIER_ID,
        "to": phone,
        "pr": "Your MegebPlus verification code is",
        "ps": "",
        "ttl": 300,
        "len": 6,
        "t": 0,
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15,
        )

        return _parse_afromessage_response(
            response,
            "SEND OTP"
        )

    except requests.RequestException as e:

        print(
            "AFROMESSAGE SEND OTP ERROR:",
            str(e)
        )

        return {
            "acknowledge": "error",
            "response": {
                "errors": [
                    f"AfroMessage request failed: {str(e)}"
                ]
            }
        }


# ============================================================
# VERIFY OTP
# ============================================================

def verify_otp(
    phone,
    otp,
    verification_id
):

    url = "https://api.afromessage.com/api/verify"

    headers = {
        "Authorization": (
            f"Bearer {settings.AFROMESSAGE_TOKEN}"
        ),
        "Accept": "application/json",
    }

    params = {
        "vc": verification_id,
        "to": phone,
        "code": otp,
    }

    try:

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15,
        )

        return _parse_afromessage_response(
            response,
            "VERIFY OTP"
        )

    except requests.RequestException as e:

        print(
            "AFROMESSAGE VERIFY OTP ERROR:",
            str(e)
        )

        return {
            "acknowledge": "error",
            "response": {
                "errors": [
                    f"AfroMessage request failed: {str(e)}"
                ]
            }
        }
