import os
import csv
import pyodbc

# CONFIGURAZIONE

CSV_DIR = "warehouse_outputkeynumeriche"  # dove abbbiamo salvato i CSV dell'Assignment 5

#connettiamoci al server
server = '131.114.50.57'
database = 'Group_ID_4_DB'
username = 'Group_ID_4'
password = '0TC5F2I9'

connectionString = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password}"
)

cnxn = pyodbc.connect(connectionString)
cursor = cnxn.cursor()

print("CONNESSO A SSMS")

# LETTURA CSV

def read_csv(filename):
    path = os.path.join(CSV_DIR, filename)
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)




# LOAD: DIMENSIONI

def load_album_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Album ON;")
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Dim_Album
            (Album_Code_PK, AlbumTitle, AlbumType)
            VALUES (?, ?, ?)
        """,
        int(r["AlbumCodePK"]),
        r["AlbumTitle"],
        r["AlbumType"],
        )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Album OFF;")
    cnxn.commit()
    print("AlbumDim caricata")


def load_artist_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Artist ON;")
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Dim_Artist
            (Artist_Code_PK, Artist_Geo_Code_FK, Name, Gender,
             Nationality)
            VALUES (?, ?, ?, ?, ?)
        """,
        int(r["ArtistCodePK"]),
        r["ArtistGeoCodeFK"],
        r["Name"],
        r["Gender"],
        r["Nationality"]
        )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Artist OFF;")
    cnxn.commit()
    print("ArtistDim caricata")

def load_artist_geo_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Artist_Geography ON;")
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Dim_Artist_Geography
            (Artist_Geo_Code_PK, H3_Code, Country, Region, Province, City)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        int(r["ArtistGeoCodePK"]),
        r["H3_index"],
        r["Country"],
        r["Region"],
        r["Province"],
        r["City"]
        )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Artist_Geography OFF;")
    cnxn.commit()
    print("ArtistGeoDim caricata")


def load_date_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Date ON;")
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Dim_Date
            (Date_Code_PK, Year, Month, Day, Season)
            VALUES (?, ?, ?, ?, ?)
        """,
        int(r["DateCodePK"]),
        r["Year"],
        r["Month"],
        r["Date_YYYYMMDD"],
        r["Season"]
        )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Date OFF;")
    cnxn.commit()
    print("DateDim caricata")


def load_symphony_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Symphony ON;")
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Dim_Symphony
            (Symphony_Code_PK, BPM, Rolloff, Flux, RMS,
             Flatness, Spectral_Complexity, Pitch, Loudness)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            int(r["SymphonyCodePK"]),
            r["BPM"],
            r["Rolloff"],
            r["Flux"],
            r["RMS"],
            r["Flatness"],
            r["Spectral_Complexity"],
            r["Pitch"],
            r["Loudness"]
                       )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Symphony OFF;")
    cnxn.commit()
    print("SymphonyDim caricata")


def load_text_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Text ON;")
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Dim_Text
            (Text_Code_PK, N_Swear_Words_IT, N_Swear_Words_EN, Is_Explicit,
             Lyrics)
            VALUES (?, ?, ?, ?, ?)
        """,
        int(r["TextCodePK"]),
        r["N_Swear_Words_IT"],
        r["N_Swear_Words_EN"],
        r["Is_Explicit"],
        r["Lyrics"]
        )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Text OFF;")
    cnxn.commit()
    print("TextDim caricata")

def load_feats_dim(rows):
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Feats ON;")
    for r in rows:
        cursor.execute("""
                    INSERT INTO dbo.Dim_Feats
                    (Feats_Code_PK)
                    VALUES (?)
                """,
                    int(r["GroupPK"])
                               )
    cursor.execute("SET IDENTITY_INSERT dbo.Dim_Feats OFF;")
    cnxn.commit()
    print("Dim_Feats caricata")

def load_feats_bridge(rows):
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.Feats_Bridge
            (Feat_Artist_Code_FK, Feats_Code_FK)
            VALUES (?, ?)
        """,
        int(r["FeaturedArtistFK"]),
        int(r["GroupFK"])
        )
    cnxn.commit()
    print("Feats_Bridge caricata")

# LOAD: FACT TABLE


def load_published_song_fact(rows):
    for r in rows:
        cursor.execute("""
            INSERT INTO dbo.PublishedSong_Fact
            (Artist_Code_FK, Album_Code_FK, Date_Code_FK,
             Symphony_Code_FK, Text_Code_FK, Feats_Code_FK,
             Track_ID,
             Title, Duration_Sec,
             Streams_First_Month, Popularity, Category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        int(r["ArtistCodeFK"]),
        int(r["AlbumCodeFK"]),
        int(r["DateCodeFK"]),
        int(r["SymphonyCodeFK"]),
        int(r["TextCodeFK"]),
        int(r["GroupFK"]),               # Feats FK

        r["Track_ID_Natural"],           # Track_ID

        r["Title"],                      # Title
        int(float(r["Duration"])) if r["Duration"] else None,  # Duration_Sec
        int(float(r["Streams_1month"])) if r["Streams_1month"] else None,
        int(float(r["Popularity"])) if r["Popularity"] else None,
        r["Category"]
        )
    cnxn.commit()
    print("Published_Song_Fact caricata")


#carichiamo tutto

def main():
    try:
        print("\n=== LETTURA CSV ===")
        album_rows      = read_csv("AlbumDim.csv")
        text_rows       = read_csv("TextDim.csv")
        artist_geo_rows = read_csv("ArtistGeoDim.csv")
        artist_rows     = read_csv("ArtistDim.csv")
        date_rows       = read_csv("DateDim.csv")
        symphony_rows   = read_csv("SymphonyDim.csv")
        feats_rows      = read_csv("GroupDim.csv")
        bridge_rows     = read_csv("GroupFeatures.csv")
        fact_rows       = read_csv("Published_Song_fact.csv")

        print("\n=== CARICAMENTO DIMENSIONI ===")
        load_album_dim(album_rows)
        load_artist_geo_dim(artist_geo_rows)
        load_artist_dim(artist_rows)
        load_date_dim(date_rows)
        load_symphony_dim(symphony_rows)
        load_text_dim(text_rows)
        load_feats_dim(feats_rows)
        load_feats_bridge(bridge_rows)

        print("\n=== CARICAMENTO FACT TABLE ===")
        load_published_song_fact(fact_rows)

        print("\n✔✔✔ TUTTO CARICATO NEL DATA WAREHOUSE ✔✔✔")

    except Exception as e:
        print("Errore durante il caricamento, facciamo rollback")
        print(e)
        cnxn.rollback()
    finally:
        cursor.close()
        cnxn.close()
        print("Connessione chiusa")

if __name__ == "__main__":
    main()