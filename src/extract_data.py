# src/extract_data.py
import os
import pandas as pd
import spotipy
import psycopg2
from auth import get_access_token


# ===============================
# CONEXÃO COM BANCO
# ===============================
def get_connection():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL não definida.")

    # garante SSL
    if "sslmode=" not in dsn:
        sep = "&" if "?" in dsn else "?"
        dsn = dsn + f"{sep}sslmode=require"

    return psycopg2.connect(dsn)


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
    all_rows = []
    after = last_timestamp

    while True:
        if after:
            results = sp.current_user_recently_played(limit=50, after=after)
        else:
            results = sp.current_user_recently_played(limit=50)

        items = results.get("items", [])
        if not items:
            break

        for item in items:
            track = item.get("track") or {}
            album = track.get("album") or {}

            artists = track.get("artists") or []
            artist = artists[0] if artists else {}

            context = item.get("context")
            context_type = context.get("type") if isinstance(context, dict) else None
            context_uri = context.get("uri") if isinstance(context, dict) else None

            all_rows.append({
                # evento
                "played_at": item.get("played_at"),

                # track
                "track_id": track.get("id"),
                "track_name": track.get("name"),
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit"),
                "track_uri": track.get("uri"),

                # artista principal
                "artist_id": artist.get("id"),
                "artist_name": artist.get("name"),
                "artist_uri": artist.get("uri"),

                # album
                "album_id": album.get("id"),
                "album_name": album.get("name"),
                "release_date": album.get("release_date"),
                "release_date_precision": album.get("release_date_precision"),
                "total_tracks": album.get("total_tracks"),
                "album_type": album.get("album_type"),
                "album_uri": album.get("uri"),

                # contexto
                "context_type": context_type,
                "context_uri": context_uri,
            })

        # paginação: usa played_at do último item retornado
        last_played = items[-1]["played_at"]
        after = int(pd.to_datetime(last_played).timestamp() * 1000)

        if len(items) < 50:
            break

    return pd.DataFrame(all_rows)


# ===============================
# UPSERT DIMENSIONS
# ===============================
def upsert_dim_artist(conn, df):
    sql = """
        INSERT INTO dim_artist (artist_id, artist_name, artist_uri)
        VALUES (%s, %s, %s)
        ON CONFLICT (artist_id)
        DO UPDATE SET
            artist_name = EXCLUDED.artist_name,
            artist_uri  = EXCLUDED.artist_uri;
    """

    rows = (
        df[["artist_id", "artist_name", "artist_uri"]]
        .dropna(subset=["artist_id"])
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()


def upsert_dim_album(conn, df):
    sql = """
        INSERT INTO dim_album (
            album_id,
            album_name,
            release_date,
            release_date_precision,
            total_tracks,
            album_type,
            album_uri
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (album_id)
        DO UPDATE SET
            album_name             = EXCLUDED.album_name,
            release_date           = EXCLUDED.release_date,
            release_date_precision = EXCLUDED.release_date_precision,
            total_tracks           = EXCLUDED.total_tracks,
            album_type             = EXCLUDED.album_type,
            album_uri              = EXCLUDED.album_uri;
    """

    rows = (
        df[[
            "album_id",
            "album_name",
            "release_date",
            "release_date_precision",
            "total_tracks",
            "album_type",
            "album_uri",
        ]]
        .dropna(subset=["album_id"])
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()


def upsert_dim_track(conn, df):
    sql = """
        INSERT INTO dim_track (
            track_id,
            track_name,
            duration_ms,
            artist_id,
            album_id,
            explicit,
            track_uri
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (track_id)
        DO UPDATE SET
            track_name  = EXCLUDED.track_name,
            duration_ms = EXCLUDED.duration_ms,
            artist_id   = EXCLUDED.artist_id,
            album_id    = EXCLUDED.album_id,
            explicit    = EXCLUDED.explicit,
            track_uri   = EXCLUDED.track_uri;
    """

    rows = (
        df[[
            "track_id",
            "track_name",
            "duration_ms",
            "artist_id",
            "album_id",
            "explicit",
            "track_uri",
        ]]
        .dropna(subset=["track_id"])
        .drop_duplicates()
        .itertuples(index=False, name=None)
    )

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()


# ===============================
# INSERT FACT
# ===============================
def insert_fact_streaming(conn, df):
    sql = """
        INSERT INTO fact_streaming (
            played_at,
            track_id,
            artist_id,
            context_type,
            context_uri
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (track_id, played_at) DO NOTHING;
    """

    rows = (
        df[["played_at", "track_id", "artist_id", "context_type", "context_uri"]]
        .dropna(subset=["played_at", "track_id"])
        .itertuples(index=False, name=None)
    )

    cur = conn.cursor()
    cur.executemany(sql, list(rows))
    cur.close()

    print(f"{len(df)} plays processados (fact_streaming).")


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

    # garante datetime
    df_new["played_at"] = pd.to_datetime(df_new["played_at"], errors="coerce")

    conn = get_connection()
    try:
        upsert_dim_artist(conn, df_new)
        upsert_dim_album(conn, df_new)
        upsert_dim_track(conn, df_new)
        insert_fact_streaming(conn, df_new)

        conn.commit()
    finally:
        conn.close()

    print("ETL finalizado com sucesso.")


if __name__ == "__main__":
    main()