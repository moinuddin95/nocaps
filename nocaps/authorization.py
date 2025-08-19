import requests
import time
import keyring
import json

AUTH0_DOMAIN = "dev-g8fu3wxgsdujf3e2.us.auth0.com"  # e.g. "dev-1234.us.auth0.com"
CLIENT_ID = "yuQNsXKeN6SHiP2LHasHdrl3MPdHB1we"
AUDIENCE = "https://nocaps.com"
SCOPE = "openid profile email offline_access"  # offline_access if you want refresh tokens

SERVICE_NAME = "mycli-auth0"   # identifier for keyring storage
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
        return resp["access_token"]
    else:
        raise Exception(f"Failed to refresh token: {resp}")

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
  if access_token:
    print("Access token found!")
  elif refresh_token:
    print("Refresh token found! Refreshing...")
    save_tokens(refresh_access_token(refresh_token))
  else:
    print("No tokens found. Starting device authorization flow...")
    device_code, interval = request_user_code()
    tokens = poll_for_tokens(device_code, interval)
    return tokens

if __name__ == "__main__":
    
    # keyring.delete_password(SERVICE_NAME, ACCESS_TOKEN_KEY)
    # keyring.delete_password(SERVICE_NAME, REFRESH_TOKEN_KEY)

    tokens = device_authorization()
    print(tokens)