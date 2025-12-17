# -*- coding: utf-8 -*-
"""
Created on Fri Dec  5 13:40:31 2025

@author: emanu
"""

import json
import csv
import xml.etree.ElementTree as ET
import os
import string 

# -------------------------------
# CONFIG
# -------------------------------
JSON_FILE = "tracks_cleaned.json"
XML_FILE = "artists_cleaned.xml"
OUTPUT_DIR = "warehouse_output_sperimentale_lyrics"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------
# SURROGATE KEY COUNTERS
# -------------------------------
counters = {
    "AlbumDim": 1,
    "TextDim": 1,
    "DateDim": 1,
    "SymphonyDim": 1,
    "ArtistGeoDim": 1,
    "ArtistDim": 1,
    "GroupDim": 1,
    "WordDim": 1  # NEW
}

def gen_key(prefix, counter):
    return f"{prefix}{counter:04d}"

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

# NEW BUFFERS FOR LYRICS
WordDim = []      # [WordCodePK, Word]
LyricsFact = []   # [TextCodeFK, WordCodeFK, PositionIndex]

# Lookup tables
album_lookup = {}
text_lookup = {}
date_lookup = {}
symphony_lookup = {}
artist_geo_lookup = {}
artist_lookup = {}   
word_lookup = {} # Maps actual word string -> WordCodePK

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

# ======================================================
# PHASE 1 : LOAD ARTISTS FROM XML
# ======================================================
print("Loading Artists...")
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

    # ArtistGeoDim
    geo_tuple = (country, region, province, city, h3)
    if geo_tuple not in artist_geo_lookup:
        pk_geo = gen_key("AGEO", counters["ArtistGeoDim"])
        counters["ArtistGeoDim"] += 1
        artist_geo_lookup[geo_tuple] = pk_geo
        ArtistGeoDim.append([pk_geo, h3, country, region, province, birth_place])
    else:
        pk_geo = artist_geo_lookup[geo_tuple]

    # ArtistDim
    if orig_artist_id not in artist_lookup:
        pk_artist = gen_key("ART", counters["ArtistDim"])
        counters["ArtistDim"] += 1
        artist_lookup[orig_artist_id] = pk_artist
        ArtistDim.append([pk_artist, pk_geo, name, gender, nationality])

# ======================================================
# PHASE 2: LOAD TRACKS JSON
# ======================================================
print("Loading Tracks...")
with open(JSON_FILE, "r", encoding="utf-8") as f:
    tracks = json.load(f)

# Punctuation remover translator
translator = str.maketrans('', '', string.punctuation)

for t in tracks:

    # ========== AlbumDim ==========
    alb_key = t["id_album"]
    if alb_key not in album_lookup:
        pk_album = gen_key("ALB", counters["AlbumDim"])
        counters["AlbumDim"] += 1
        album_lookup[alb_key] = pk_album
        AlbumDim.append([pk_album, t.get("album_name", ""), t.get("album_type", ""), t.get("album_release_date", "")])
    else:
        pk_album = album_lookup[alb_key]

    # ========== TextDim (Metadata Only) ==========
    txt_key = t["id"]
    if txt_key not in text_lookup:
        pk_text = gen_key("TXT", counters["TextDim"])
        counters["TextDim"] += 1
        text_lookup[txt_key] = pk_text
        
        # NOTE: Removed "Lyrics" from here
        TextDim.append([
            pk_text, t.get("n_sentences",""), t.get("n_tokens",""),
            t.get("Is_Explicit",""), t.get("N_Swear_Words_IT",""),
            t.get("N_Swear_Words_EN","")
        ])

        # ========== LYRICS PROCESSING (WordDim + Bridge) ==========
        raw_lyrics = t.get("Lyrics")
        print(raw_lyrics,"ii")
        if raw_lyrics:
            # 1. Clean and split
            # Lowercase -> Remove Punctuation -> Split by whitespace
            clean_lyrics = raw_lyrics.lower().split()
            print(clean_lyrics)
            # 2. Iterate words
            for idx, word in enumerate(clean_lyrics):
                if not word: continue
                
                # Check/Add to WordDim
                if word not in word_lookup:
                    pk_word = gen_key("WRD", counters["WordDim"])
                    counters["WordDim"] += 1
                    word_lookup[word] = pk_word
                    WordDim.append([pk_word, word])
                else:
                    pk_word = word_lookup[word]
                
                # Add to Fact Table (TextFK, WordFK, Position)
                # Position is idx + 1 (1-based index is standard for business logic)
                LyricsFact.append([pk_text, pk_word, idx+1])

    else:
        pk_text = text_lookup[txt_key]

    # ========== DateDim ==========
    date_key = (t["year_yyyy"], t["month_yyyymm"], t["day_yyyymmdd"])
    if date_key not in date_lookup:
        pk_date = gen_key("DAT", counters["DateDim"])
        counters["DateDim"] += 1
        date_lookup[date_key] = pk_date

        year_str = f"{int(t['year_yyyy']):04d}" if t["year_yyyy"] else None
        month_str = f"{int(t['year_yyyy']):04d}{int(t['month_yyyymm']):02d}" if (t["year_yyyy"] and t["month_yyyymm"]) else None
        day_str = f"{int(t['year_yyyy']):04d}{int(t['month_yyyymm']):02d}{int(t['day_yyyymmdd']):02d}" if (t["year_yyyy"] and t["month_yyyymm"] and t["day_yyyymmdd"]) else None

        DateDim.append([pk_date, year_str, month_str, day_str, t.get("season","")])
    else:
        pk_date = date_lookup[date_key]

    # ========== SymphonyDim ==========
    sym_key = t["id"]
    if sym_key not in symphony_lookup:
        pk_sym = gen_key("SYM", counters["SymphonyDim"])
        counters["SymphonyDim"] += 1
        symphony_lookup[sym_key] = pk_sym
        SymphonyDim.append([
            pk_sym, t.get("bpm",""), t.get("rolloff",""), t.get("flux",""),
            t.get("rms",""), t.get("flatness",""), t.get("spectral_complexity",""),
            t.get("pitch",""), t.get("loudness","")
        ])
    else:
        pk_sym = symphony_lookup[sym_key]

    # ========== GroupDim ==========
    pk_group = gen_key("GRP", counters["GroupDim"])
    counters["GroupDim"] += 1
    GroupDim.append([pk_group])

    # ========== GroupFeatures ==========
    feats = [x.strip() for x in t.get("featured_artists", "").split(",")] if t.get("featured_artists") else []
    for f in feats:
        if not f: continue
        
        # Simple name matching (Note: In production, IDs are safer)
        matched_artist_pk = None
        for row in ArtistDim:
            if row[2].strip().lower() == f.lower(): 
                matched_artist_pk = row[0]
                break
        
        if matched_artist_pk:
            GroupFeatures.append([pk_group, matched_artist_pk])

    # ========== PublishedFact ==========
    orig_artist_id = t.get("id_artist")
    pk_artist = artist_lookup.get(orig_artist_id, None)

    PublishedFact.append([
        t["id"],
        t.get("title",""),
        t.get("duration_ms",""),
        t.get("streams@1month",""),
        t.get("popularity",""),
        t.get("category",""),
        pk_artist,
        pk_album,
        pk_date,
        pk_sym,
        pk_text,
        pk_group
    ])

# ======================================================
# WRITE CSV FILES
# ======================================================
write_csv("AlbumDim.csv", ["AlbumCodePK","AlbumTitle","AlbumType"], AlbumDim)
# Modified TextDim Header
write_csv("TextDim.csv", ["TextCodePK","n_sentences","n_tokens","Is_Explicit","N_Swear_Words_IT","N_Swear_Words_EN"], TextDim)
write_csv("ArtistGeoDim.csv", ["ArtistGeoCodePK","H3_index","Country","Region","Province","City"], ArtistGeoDim)
write_csv("ArtistDim.csv", ["ArtistCodePK","ArtistGeoCodeFK","Name","Gender","Nationality"], ArtistDim)
write_csv("DateDim.csv", ["DateCodePK","Year","Month","Day","Season"], DateDim)
write_csv("SymphonyDim.csv", ["SymphonyCodePK","BPM","Rolloff","Flux","RMS","Flatness","Spectral_Complexity","Pitch","Loudness"], SymphonyDim)
write_csv("GroupDim.csv", ["GroupPK"], GroupDim)
write_csv("GroupFeatures.csv", ["GroupFK","FeaturedArtistFK"], GroupFeatures)
write_csv("Published_Song_fact.csv",
          ["Track_ID","Title","Duration",
           "Streams_1month","Popularity","Category",
           "ArtistCodeFK","AlbumCodeFK","DateCodeFK","SymphonyCodeFK","TextCodeFK","GroupFK"],
          PublishedFact)

# NEW CSV WRITE
write_csv("WordDim.csv", ["WordCodePK", "Word"], WordDim)
write_csv("Lyrics_Bridge_Fact.csv", ["TextCodeFK", "WordCodeFK", "WordPosition"], LyricsFact)

print("\nDONE! Warehouse generated with Tokenized Lyrics.")