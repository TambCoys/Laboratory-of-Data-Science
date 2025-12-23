# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 15:29:16 2025

@author: emanu
"""
import json
import csv
import xml.etree.ElementTree as ET
import os

# -------------------------------
# CONFIG
# -------------------------------
JSON_FILE = "tracks_cleaned.json"
XML_FILE = "artists_cleaned.xml"
OUTPUT_DIR = "warehouse_outputkeynumeriche!"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# SURROGATE KEY COUNTERS (INTEGERS)
# -------------------------------
# We initialize all counters to 1.
# These will be the Primary Keys (INT) for our tables.
counters = {
    "AlbumDim": 1,
    "TextDim": 1,
    "DateDim": 1,
    "SymphonyDim": 1,
    "ArtistGeoDim": 1,
    "ArtistDim": 1,
    "GroupDim": 1,
    "PublishedFact": 1  # Added counter for Fact Table PK
}

# -------------------------------
# BUFFERS
# -------------------------------
AlbumDim = []
TextDim = []
DateDim = []
SymphonyDim = []
ArtistGeoDim = []
ArtistDim = []
GroupDim = []
GroupFeatures = []
PublishedFact = []

# -------------------------------
# LOOKUP TABLES (Natural -> Integer Surrogate)
# -------------------------------
album_lookup = {}       # id_album -> int
text_lookup = {}        # track_id -> int
date_lookup = {}        # (y,m,d) -> int
symphony_lookup = {}    # track_id -> int
artist_geo_lookup = {}  # (country, region...) -> int
artist_lookup = {}      # id_author -> int
artist_name_lookup = {} # name -> int (For resolving features by name)
group_lookup = {}       # track_id -> int (Since Group is 1:1 with Track)

# -------------------------------
# HELPER: WRITE CSV
# -------------------------------
def write_csv(filename, header, rows):
    path = os.path.join(OUTPUT_DIR, filename)
    print(f"Writing {len(rows)} rows to {filename}...")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

# -------------------------------
# HELPER: SEASON
# -------------------------------
def determine_season(month):
    if month != None:
        try:
            m = int(month)
            if m in [12, 1, 2]: return "Winter"
            if m in [3, 4, 5]: return "Spring"
            if m in [6, 7, 8]: return "Summer"
        except:
            pass
    return "Autumn"

# ======================================================
# PHASE 1 : LOAD ARTISTS FROM XML → ArtistDim + ArtistGeoDim
# ======================================================
print("Processing XML (Artists)...")
tree = ET.parse(XML_FILE)
root = tree.getroot()

for row in root.findall(".//row"):
    orig_artist_id = row.findtext("id_author")

    # Artist attributes
    name = row.findtext("name")
    gender = row.findtext("gender")
    birth_date = row.findtext("birth_date")
    birth_place = row.findtext("birth_place")
    nationality = row.findtext("nationality")

    # Geo attributes
    country = row.findtext("country")
    region = row.findtext("region")
    province = row.findtext("province")
    city = row.findtext("province")  # fallback
    h3 = row.findtext("h3_idx")

    # --- ArtistGeoDim (Surrogate INT) ---
    geo_tuple = (country, region, province, city, h3)
    if geo_tuple not in artist_geo_lookup:
        pk_geo = counters["ArtistGeoDim"]
        counters["ArtistGeoDim"] += 1
        
        artist_geo_lookup[geo_tuple] = pk_geo
        ArtistGeoDim.append([pk_geo, h3, country, region, province, birth_place])
    else:
        pk_geo = artist_geo_lookup[geo_tuple]

    # --- ArtistDim (Surrogate INT) ---
    if orig_artist_id not in artist_lookup:
        pk_artist = counters["ArtistDim"]
        counters["ArtistDim"] += 1
        
        artist_lookup[orig_artist_id] = pk_artist
        # Store name mapping for Feature matching later
        if name:
            artist_name_lookup[name.strip().lower()] = pk_artist
            
        ArtistDim.append([pk_artist, pk_geo, name, gender, nationality])

# ======================================================
# PHASE 2: LOAD TRACKS JSON
# ======================================================
print("Processing JSON (Tracks)...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    tracks = json.load(f)

for t in tracks:
    track_id = t["id"]

    # ========== AlbumDim (Surrogate INT) ==========
    alb_key = t["id_album"]
    if alb_key not in album_lookup:
        pk_album = counters["AlbumDim"]
        counters["AlbumDim"] += 1
        
        album_lookup[alb_key] = pk_album
        AlbumDim.append([pk_album, t.get("album_name", ""), t.get("album_type", ""), t.get("album_release_date", "")])
    else:
        pk_album = album_lookup[alb_key]

    # ========== TextDim (Surrogate INT) ==========

    txt_key = t["id"]
    if txt_key not in text_lookup:
        pk_text = counters["TextDim"]
        counters["TextDim"] += 1

        text_lookup[txt_key] = pk_text
        lyrics_raw = t.get("lyrics", "") or ""
        lyrics_clean = lyrics_raw.replace("\n", " ").replace("\r", " ")

        TextDim.append([
            pk_text,
            t.get("swear_IT", ""),
            t.get("swear_IT", ""),
            t.get("swear_IT", ""),
            t.get("swear_EN", ""),
            t.get("explicit", ""),
            lyrics_clean
        ])
    else:
        pk_text = text_lookup[txt_key]
    # ========== DateDim (Surrogate INT) ==========
    # Key is (Year, Month, Day)
    y_raw, m_raw, d_raw = t["year"], t["month"], t["day"]
    date_key = (y_raw, m_raw, d_raw)
    
    if date_key not in date_lookup:
        pk_date = counters["DateDim"]
        counters["DateDim"] += 1
        date_lookup[date_key] = pk_date

        # Format strings for CSV
        try:
            year_str = f"{int(y_raw):04d}" if y_raw is not None else None
            month_str = f"{int(y_raw):04d}{int(m_raw):02d}" if (y_raw is not None and m_raw is not None) else None
            day_str = f"{int(y_raw):04d}{int(m_raw):02d}{int(d_raw):02d}" if (y_raw is not None and m_raw is not None and d_raw is not None) else None
        except:
            year_str, month_str, day_str = None, None, None

        DateDim.append([pk_date, day_str, year_str, month_str, determine_season(m_raw)])
    else:
        pk_date = date_lookup[date_key]

    # ========== SymphonyDim (Surrogate INT) ==========
    if track_id not in symphony_lookup:
        pk_sym = counters["SymphonyDim"]
        counters["SymphonyDim"] += 1
        
        symphony_lookup[track_id] = pk_sym
        SymphonyDim.append([
            pk_sym, t.get("bpm",""), t.get("rolloff",""), t.get("flux",""),
            t.get("rms",""), t.get("flatness",""), t.get("spectral_complexity",""),
            t.get("pitch",""), t.get("loudness","")
        ])
    else:
        pk_sym = symphony_lookup[track_id]

    # =====================================================
    # GROUPDIM (Surrogate INT)
    # =====================================================
    pk_group = counters["GroupDim"]
    counters["GroupDim"] += 1
    # Store this group PK for this track
    group_lookup[track_id] = pk_group
    
    GroupDim.append([pk_group])

    # =====================================================
    # GROUPFEATURES
    # =====================================================
    feats = [x.strip() for x in t.get("featured_artists", "").split(",")] if t.get("featured_artists") else []

    for f in feats:
        if not f: continue

        # Lookup Artist INT ID by Name
        # We use the dictionary we built in Phase 1 for O(1) speed
        matched_artist_pk = artist_name_lookup.get(f.strip().lower())

        if matched_artist_pk:
             # Link Group (Int) to Artist (Int)
            GroupFeatures.append([pk_group, matched_artist_pk])

    # =====================================================
    # FACT TABLE (Surrogate INT PK)
    # =====================================================
    orig_artist_id = t.get("id_artist")
    pk_artist = artist_lookup.get(orig_artist_id, None)
    
    pk_fact = counters["PublishedFact"]
    counters["PublishedFact"] += 1

    PublishedFact.append([
        pk_fact,              # Surrogate PK (Int)
        t["id"],              # Natural ID (String) kept as attribute
        t.get("title",""),
        t.get("duration_ms",""),
        t.get("streams@1month",""),
        t.get("popularity",""),
        t.get("category",""),
        pk_artist,            # FK Int
        pk_album,             # FK Int
        pk_date,              # FK Int
        pk_sym,               # FK Int
        pk_text,              # FK Int
        pk_group              # FK Int
    ])

# ======================================================
# WRITE CSV FILES
# ======================================================
print("Writing CSVs...")

write_csv("AlbumDim.csv", 
          ["AlbumCodePK","AlbumTitle","AlbumType","AlbumReleaseDate"], 
          AlbumDim)

write_csv("TextDim.csv", 
          ["TextCodePK","Is_Explicit","N_Swear_Words_IT","N_Swear_Words_EN", "Lyrics"], 
          TextDim)

write_csv("ArtistGeoDim.csv", 
          ["ArtistGeoCodePK","H3_index","Country","Region","Province","City"], 
          ArtistGeoDim)

write_csv("ArtistDim.csv", 
          ["ArtistCodePK","ArtistGeoCodeFK","Name","Gender","Nationality"], 
          ArtistDim)

write_csv("DateDim.csv", 
          ["DateCodePK", "Date_YYYYMMDD", "Year", "Month", "Season"], 
          DateDim)

write_csv("SymphonyDim.csv", 
          ["SymphonyCodePK","BPM","Rolloff","Flux","RMS","Flatness","Spectral_Complexity","Pitch","Loudness"], 
          SymphonyDim)

write_csv("GroupDim.csv", 
          ["GroupPK"], 
          GroupDim)

write_csv("GroupFeatures.csv", 
          ["GroupFK","FeaturedArtistFK"], 
          GroupFeatures)

write_csv("Published_Song_fact.csv",
          ["PublishedSong_Fact_PK", "Track_ID_Natural", "Title", "Duration",
           "Streams_1month","Popularity","Category",
           "ArtistCodeFK","AlbumCodeFK","DateCodeFK","SymphonyCodeFK","TextCodeFK","GroupFK"],
          PublishedFact)

print("DONE! All warehouse tables generated with Integer Surrogate Keys.")