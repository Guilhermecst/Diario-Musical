import os
import base64
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

# Scopes mínimos pro seu projeto atual (recently played)
SCOPES = "user-read-recently-played"


def build_auth_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        # força tela de consentimento para garantir refresh_token novo
        "show_dialog": "true",
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_tokens(code: str):
    auth_str = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }

    resp = requests.post(TOKEN_URL, headers=headers, data=data)
    if resp.status_code != 200:
        print("Erro ao trocar code por token:", resp.status_code, resp.text)
        resp.raise_for_status()

    return resp.json()


def main():
    if not CLIENT_ID or not CLIENT_SECRET:
        raise RuntimeError("Defina SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET no .env")

    print("\n1) Abra esta URL no navegador e autorize:")
    print(build_auth_url())

    print("\n2) Depois de autorizar, você será redirecionado para uma URL assim:")
    print("   http://127.0.0.1:8888/callback?code=XXXX")
    code = input("\nCole aqui o valor do 'code': ").strip()

    tokens = exchange_code_for_tokens(code)

    print("\n✅ Tokens obtidos:")
    print("access_token:", tokens.get("access_token")[:20] + "...")
    print("refresh_token:", tokens.get("refresh_token"))
    print("\n➡️ Copie o refresh_token e coloque em SPOTIFY_REFRESH_TOKEN (GitHub Secrets e/ou .env).")


if __name__ == "__main__":
    main()