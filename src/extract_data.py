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
            artist = track["artists"][0]

            all_tracks.append({
                "played_at": item["played_at"],
                "track_id": track["id"],
                "track_name": track["name"],
                "artist_id": artist["id"],
                "artist_name": artist["name"],
                "album_name": track["album"]["name"],
                "duration_ms": track["duration_ms"]
            })

        last_played = items[-1]["played_at"]
        after = int(pd.to_datetime(last_played).timestamp() * 1000)

        if len(items) < 50:
            break

    return pd.DataFrame(all_tracks)

# ===============================
# UPSERT NO BANCO
# ===============================

def upsert_dim_artist(conn, df):

    sql = """
        INSERT INTO dim_artist (artist_id, artist_name)
        VALUES (%s, %s)
        ON CONFLICT (artist_id)
        DO UPDATE SET artist_name = EXCLUDED.artist_name;
    """

    rows = df[["artist_id", "artist_name"]].drop_duplicates() \
        .itertuples(index=False, name=None)

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()

def upsert_dim_track(conn, df):

    sql = """
        INSERT INTO dim_track (
            track_id,
            track_name,
            album_name,
            duration_ms,
            artist_id
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (track_id)
        DO UPDATE SET
            track_name = EXCLUDED.track_name,
            album_name = EXCLUDED.album_name,
            duration_ms = EXCLUDED.duration_ms,
            artist_id = EXCLUDED.artist_id;
    """

    rows = df[[
        "track_id",
        "track_name",
        "album_name",
        "duration_ms",
        "artist_id"
    ]].drop_duplicates().itertuples(index=False, name=None)

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()

# ===============================
# INSERÇÃO NO BANCO
# ===============================

def insert_tracks_into_db(conn, df):

    sql = """
        INSERT INTO fact_streaming (
            played_at,
            track_id,
            track_name,
            artist_name,
            album_name,
            duration_ms,
            artist_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_id, played_at) DO NOTHING;
    """

    rows = df[[
        "played_at",
        "track_id",
        "track_name",
        "artist_name",
        "album_name",
        "duration_ms",
        "artist_id"
    ]].itertuples(index=False, name=None)

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()

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

    conn = get_connection()
    try:
        # 1) sobe dimensões
        upsert_dim_artist(conn, df_new)
        upsert_dim_track(conn, df_new)

        # 2) sobe fato
        insert_tracks_into_db(conn, df_new)

        # 3) persiste tudo
        conn.commit()
    finally:
        conn.close()

    print("ETL finalizado com sucesso.")