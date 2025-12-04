import os
import csv
import pyodbc

# =========================
# CONFIGURAZIONE
# =========================

CSV_DIR = "warehouse_output"  # dove abbbiamo salvato i CSV dell'Assignment 5

conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=131.114.50.57;"
    "DATABASE=Group_ID_4_DB;"
    "UID=Group_ID_4;"
    "PWD=0TC5F2I9;"
)
cursor = conn.cursor()
print("✔ Connessione al database stabilita")

# =========================
# FUNZIONI PER LEGGERE I CSV
# =========================

def read_csv(filename):
    path = os.path.join(CSV_DIR, filename)
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def read_csv_raw(filename):
    """
    Per SongsFeatures.csv: il tuo Assignment 5 scrive 3 colonne
    [FeatureCodePK, track_natural_id, featured_artist_name]
    ma l'header ha solo 2 nomi.
    Qui leggo come righe raw.
    """
    path = os.path.join(CSV_DIR, filename)
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)  # salta intestazione
        return [row for row in reader]

# =========================
# LOAD: DIMENSIONI
# =========================

def load_album_dim(rows):
    for r in rows:
        cursor.execute("""
            INSERT INTO AlbumDim
            (AlbumCodePK, Title, Type, ReleaseDate)
            VALUES (?, ?, ?, ?)
        """,
        r["AlbumCodePK"],
        r["Title"],
        r["Type"],
        r["ReleaseDate"]
        )
    conn.commit()
    print("✔ AlbumDim caricata")


def load_text_dim(rows):
    for r in rows:
        # conversioni minime numeriche
        n_sent = int(r["N_Sentences"]) if r["N_Sentences"] not in ("", "None") else None
        n_tok  = int(r["N_Tokens"])    if r["N_Tokens"]    not in ("", "None") else None
        cpt    = float(r["Char_Per_Tok"]) if r["Char_Per_Tok"] not in ("", "None") else None
        atpc   = float(r["Avg_Token_Per_Clause"]) if r["Avg_Token_Per_Clause"] not in ("", "None") else None
        is_exp = int(r["Is_Explicit"]) if r["Is_Explicit"] not in ("", "None") else 0

        cursor.execute("""
            INSERT INTO TextDim
            (TextCodePK, N_Sentences, N_Tokens, Char_Per_Tok,
             Avg_Token_Per_Clause, Is_Explicit)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        r["TextCodePK"],
        n_sent,
        n_tok,
        cpt,
        atpc,
        is_exp
        )
    conn.commit()
    print("✔ TextDim caricata")


def load_artist_geo_dim(rows):
    for r in rows:
        cursor.execute("""
            INSERT INTO ArtistGeoDim
            (ArtistGeoCodePK, H3_index, Country, Region, Province, City)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        r["ArtistGeoCodePK"],
        r["H3_index"],
        r["Country"],
        r["Region"],
        r["Province"],
        r["City"]
        )
    conn.commit()
    print("✔ ArtistGeoDim caricata")


def load_artist_dim(rows):
    for r in rows:
        birth_fk = int(r["ArtistBirthDateFK"]) if r["ArtistBirthDateFK"] not in ("", "None") else None

        cursor.execute("""
            INSERT INTO ArtistDim
            (ArtistCodePK, ArtistGeoCodeFK, Name, Gender,
             ArtistBirthDateFK, BirthPlace, Nationality)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        r["ArtistCodePK"],
        r["ArtistGeoCodeFK"],
        r["Name"],
        r["Gender"],
        birth_fk,
        r["BirthPlace"],
        r["Nationality"]
        )
    conn.commit()
    print("✔ ArtistDim caricata")


def load_date_dim(rows):
    for r in rows:
        date_int = None if r["DateInt"] in ("", "NULL", "None") else int(r["DateInt"])
        year     = None if r["Year"]    in ("", "NULL", "None") else int(r["Year"])
        month    = None if r["Month"]   in ("", "NULL", "None") else int(r["Month"])

        cursor.execute("""
            INSERT INTO DateDim
            (DateCodePK, DateInt, Year, Month, Season)
            VALUES (?, ?, ?, ?, ?)
        """,
        r["DateCodePK"],
        date_int,
        year,
        month,
        r["Season"]
        )
    conn.commit()
    print("✔ DateDim caricata")


def load_symphony_dim(rows):
    for r in rows:
        bpm   = float(r["BPM"])   if r["BPM"]   not in ("", "None") else None
        roll  = float(r["Rolloff"]) if r["Rolloff"] not in ("", "None") else None
        flux  = float(r["Flux"])  if r["Flux"]  not in ("", "None") else None
        rms   = float(r["RMS"])   if r["RMS"]   not in ("", "None") else None
        flat  = float(r["Flatness"]) if r["Flatness"] not in ("", "None") else None
        spec  = float(r["Spectral_Complexity"]) if r["Spectral_Complexity"] not in ("", "None") else None
        pitch = float(r["Pitch"]) if r["Pitch"] not in ("", "None") else None
        loud  = float(r["Loudness"]) if r["Loudness"] not in ("", "None") else None

        cursor.execute("""
            INSERT INTO SymphonyDim
            (SymphonyCodePK, BPM, Rolloff, Flux, RMS,
             Flatness, Spectral_Complexity, Pitch, Loudness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        r["SymphonyCodePK"],
        bpm,
        roll,
        flux,
        rms,
        flat,
        spec,
        pitch,
        loud
        )
    conn.commit()
    print("✔ SymphonyDim caricata")


def load_songs_features(rows_raw):
    """
    rows_raw: lista di liste
    r[0] = FeatureCodePK
    r[1] = TrackID originale (dal tuo Assignment 5)
    r[2] = FeaturedArtistName (o None)
    """
    for r in rows_raw:
        feature_pk = r[0]
        track_id   = r[1]
        feat_name  = r[2] if len(r) > 2 else None

        cursor.execute("""
            INSERT INTO SongsFeatures
            (FeatureCodePK, TrackID_Original, FeaturedArtistName)
            VALUES (?, ?, ?)
        """,
        feature_pk,
        track_id,
        feat_name
        )
    conn.commit()
    print("✔ SongsFeatures caricata")

# =========================
# LOAD: FACT TABLE
# =========================

def load_published_song_fact(rows):
    for r in rows:
        duration = int(r["Duration"])        if r["Duration"]        not in ("", "None") else None
        streams  = int(r["Streams_1month"])  if r["Streams_1month"]  not in ("", "None") else None
        pop      = int(r["Popularity"])      if r["Popularity"]      not in ("", "None") else None

        artist_fk  = int(r["ArtistCodeFK"])   if r["ArtistCodeFK"]   not in ("", "None") else None
        album_fk   = int(r["AlbumCodeFK"])    if r["AlbumCodeFK"]    not in ("", "None") else None
        date_fk    = int(r["DateCodeFK"])     if r["DateCodeFK"]     not in ("", "None") else None
        sym_fk     = int(r["SymphonyCodeFK"]) if r["SymphonyCodeFK"] not in ("", "None") else None
        text_fk    = int(r["TextCodeFK"])     if r["TextCodeFK"]     not in ("", "None") else None
        feat_fk    = int(r["FeatureCodeFK"])  if r["FeatureCodeFK"]  not in ("", "None") else None

        cursor.execute("""
            INSERT INTO Published_Song_fact
            (Title, Language, Duration,
             Streams_1month, Popularity,
             ArtistCodeFK, AlbumCodeFK, DateCodeFK,
             SymphonyCodeFK, TextCodeFK, FeatureCodeFK)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        r["Title"],
        r["Language"],
        duration,
        streams,
        pop,
        artist_fk,
        album_fk,
        date_fk,
        sym_fk,
        text_fk,
        feat_fk
        )
    conn.commit()
    print("✔ Published_Song_fact caricata")

# =========================
# MAIN: ORDINE DI CARICAMENTO
# =========================

def main():
    try:
        print("\n=== LETTURA CSV ===")
        album_rows      = read_csv("AlbumDim.csv")
        text_rows       = read_csv("TextDim.csv")
        artist_geo_rows = read_csv("ArtistGeoDim.csv")
        artist_rows     = read_csv("ArtistDim.csv")
        date_rows       = read_csv("DateDim.csv")
        symphony_rows   = read_csv("SymphonyDim.csv")
        songsfeat_rows  = read_csv_raw("SongsFeatures.csv")
        fact_rows       = read_csv("Published_Song_fact.csv")

        print("\n=== CARICAMENTO DIMENSIONI ===")
        load_album_dim(album_rows)
        load_text_dim(text_rows)
        load_artist_geo_dim(artist_geo_rows)
        load_artist_dim(artist_rows)
        load_date_dim(date_rows)
        load_symphony_dim(symphony_rows)
        load_songs_features(songsfeat_rows)

        print("\n=== CARICAMENTO FACT TABLE ===")
        load_published_song_fact(fact_rows)

        print("\n✔✔✔ TUTTO CARICATO NEL DATA WAREHOUSE ✔✔✔")
    except Exception as e:
        print("❌ Errore durante il caricamento, faccio rollback")
        print(e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("Connessione chiusa.")

main()
