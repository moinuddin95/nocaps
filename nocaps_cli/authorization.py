import requests
import time
import keyring
import json
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")  # e.g. "dev-1234.us.auth0.com"
CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUDIENCE = os.getenv("AUTH0_AUDIENCE")
SCOPE = os.getenv("AUTH0_SCOPE")

SERVICE_NAME = "nocaps-auth0"   # identifier for keyring storage
ACCESS_TOKEN_KEY = "access_token"
REFRESH_TOKEN_KEY = "refresh_token"

def save_tokens(access_token, refresh_token = None):
    keyring.set_password(SERVICE_NAME, ACCESS_TOKEN_KEY, access_token)
    if refresh_token:
        keyring.set_password(SERVICE_NAME, REFRESH_TOKEN_KEY, refresh_token)

def load_tokens():
    access_token = keyring.get_password(SERVICE_NAME, ACCESS_TOKEN_KEY)
    refresh_token = keyring.get_password(SERVICE_NAME, REFRESH_TOKEN_KEY)
    return access_token, refresh_token

def refresh_access_token(refresh_token):
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    data = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    resp = requests.post(url, data=data).json()
    if "access_token" in resp:
        save_tokens(resp["access_token"])
    else:
        device_code, interval = request_user_code()
        poll_for_tokens(device_code, interval)

def request_user_code():
    url = f"https://{AUTH0_DOMAIN}/oauth/device/code"
    data = {
        "client_id": CLIENT_ID,
        "scope": SCOPE,
        "audience": AUDIENCE
    }
    resp = requests.post(url, data=data).json()

    if "error" in resp:
        raise Exception(f"Failed to request user code: {resp}")

    device_code = resp["device_code"]
    user_code = resp["user_code"]
    verification_uri_complete = resp["verification_uri_complete"]
    interval = resp.get("interval", 5)

    print(f"Please visit {verification_uri_complete} and enter the code: {user_code}")

    return device_code, interval

def poll_for_tokens(device_code, interval):
    token_url = f"https://{AUTH0_DOMAIN}/oauth/token"
    while True:
        time.sleep(interval)
        token_data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": CLIENT_ID
        }
        token_resp = requests.post(token_url, data=token_data).json()

        if "error" in token_resp:
            if token_resp["error"] == "authorization_pending":
                print("Waiting for user to authorize...")
                continue
            elif token_resp["error"] == "slow_down":
                interval += 5
                continue
            else:
                raise Exception(f"Auth failed: {token_resp}")
        else:
            print("✅ Auth successful!")
            save_tokens(token_resp["access_token"], token_resp.get("refresh_token"))
            return token_resp  # contains access_token, refresh_token (if requested)

def device_authorization():
  access_token, refresh_token = load_tokens()
  if access_token and refresh_token:
    return
  elif not access_token and refresh_token:
    save_tokens(refresh_access_token(refresh_token))
  else:
    device_code, interval = request_user_code()
    poll_for_tokens(device_code, interval)

if __name__ == "__main__":
    
    keyring.delete_password(SERVICE_NAME, ACCESS_TOKEN_KEY)
    keyring.delete_password(SERVICE_NAME, REFRESH_TOKEN_KEY)

    # tokens = device_authorization()
    # print(tokens)