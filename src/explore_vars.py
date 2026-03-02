import json
from dotenv import load_dotenv
import spotipy
from auth import get_access_token

load_dotenv()  # carrega variáveis do .env (uso local)

def main():
    access_token = get_access_token()
    sp = spotipy.Spotify(auth=access_token)

    results = sp.current_user_recently_played(limit=1)

    item = results["items"][0]

    print(json.dumps(item, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()