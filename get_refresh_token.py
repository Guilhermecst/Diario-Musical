import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

scope = "user-read-recently-played user-top-read"

sp_oauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
    scope=scope
)

token_info = sp_oauth.get_access_token(as_dict=True)

print("ACCESS TOKEN:")
print(token_info["access_token"])
print("\nREFRESH TOKEN:")
print(token_info["refresh_token"])