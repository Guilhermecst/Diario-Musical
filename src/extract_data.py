import os
import pandas as pd
import spotipy
import psycopg2
from datetime import datetime
from auth import get_access_token


# ===============================
# CONEXÃO COM BANCO
# ===============================

def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# ===============================
# BUSCAR ÚLTIMO TIMESTAMP NO BANCO
# ===============================

def get_last_timestamp_from_db():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT MAX(played_at) FROM fact_streaming;")
    result = cur.fetchone()[0]

    cur.close()
    conn.close()

    if result:
        return int(result.timestamp() * 1000)

    return None


# ===============================
# EXTRAÇÃO DA API
# ===============================

def fetch_recent_tracks(sp, last_timestamp=None):

    all_tracks = []
    after = last_timestamp

    while True:

        if after:
            results = sp.current_user_recently_played(
                limit=50,
                after=after
            )
        else:
            results = sp.current_user_recently_played(limit=50)

        items = results["items"]

        if not items:
            break

        for item in items:

            track = item["track"]

            all_tracks.append({
                "played_at": item["played_at"],
                "track_id": track["id"],
                "track_name": track["name"],
                "artist_name": track["artists"][0]["name"],
                "album_name": track["album"]["name"],
                "duration_ms": track["duration_ms"]
            })

        last_played = items[-1]["played_at"]
        after = int(pd.to_datetime(last_played).timestamp() * 1000)

        if len(items) < 50:
            break

    return pd.DataFrame(all_tracks)


# ===============================
# INSERÇÃO NO BANCO
# ===============================

def insert_tracks_into_db(df):

    conn = get_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO fact_streaming (
            played_at,
            track_id,
            track_name,
            artist_name,
            album_name,
            duration_ms
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_id, played_at) DO NOTHING;
    """

    for _, row in df.iterrows():
        cur.execute(insert_query, (
            row["played_at"],
            row["track_id"],
            row["track_name"],
            row["artist_name"],
            row["album_name"],
            row["duration_ms"]
        ))

    conn.commit()
    cur.close()
    conn.close()

    print(f"{len(df)} registros processados.")


# ===============================
# MAIN
# ===============================

def main():

    print("Iniciando ETL...")

    access_token = get_access_token()
    sp = spotipy.Spotify(auth=access_token)

    last_timestamp = get_last_timestamp_from_db()

    df_new = fetch_recent_tracks(sp, last_timestamp)

    if df_new.empty:
        print("Nenhuma música nova encontrada.")
        return

    df_new["played_at"] = pd.to_datetime(df_new["played_at"])

    insert_tracks_into_db(df_new)

    print("ETL finalizado com sucesso.")


if __name__ == "__main__":
    main()