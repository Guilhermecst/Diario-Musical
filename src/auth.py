import os
import base64
import requests


def get_access_token():
    client_id = os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")
    refresh_token = os.getenv("SPOTIPY_REFRESH_TOKEN")

    auth_str = f"{client_id}:{client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers=headers,
        data=data
    )

    response.raise_for_status()  # falha se der erro

    return response.json()["access_token"]