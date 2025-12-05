# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 18:30:17 2025

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
OUTPUT_DIR = "warehouse_output"

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
    "GroupDim": 1
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

# Lookup tables
album_lookup = {}
text_lookup = {}
date_lookup = {}
symphony_lookup = {}
artist_geo_lookup = {}
artist_lookup = {}   # original XML id_author → ArtistDim surrogate key

# -------------------------------
# HELPER: WRITE CSV
# -------------------------------
def write_csv(filename, header, rows):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(
            f,
            delimiter=";",          # <-- separatore di colonna
            quotechar='"',          # <-- testo racchiuso tra "
            quoting=csv.QUOTE_MINIMAL
        )
        w.writerow(header)
        for r in rows:
            w.writerow(r)


# ======================================================
# PHASE 1 : LOAD ARTISTS FROM XML → ArtistDim + ArtistGeoDim
# ======================================================
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
        ArtistDim.append([pk_artist, pk_geo, name, gender, birth_date, birth_place, nationality])

# ======================================================
# PHASE 2: LOAD TRACKS JSON
# ======================================================
with open(JSON_FILE, "r", encoding="utf-8") as f:
    tracks = json.load(f)

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

    # ========== TextDim ==========
    txt_key = t["id"]
    if txt_key not in text_lookup:
        pk_text = gen_key("TXT", counters["TextDim"])
        counters["TextDim"] += 1
        text_lookup[txt_key] = pk_text
        lyrics_raw = t.get("lyrics", "") or ""
        lyrics_clean = lyrics_raw.replace("\n", " ").replace("\r", " ")

        TextDim.append([
            pk_text,
            t.get("swear_IT", ""),
            t.get("swear_EN", ""),
            t.get("explicit", ""),
            lyrics_clean
        ])
    else:
        pk_text = text_lookup[txt_key]

    # ========== DateDim ==========
    # uso solo i campi già calcolati nel JSON
    date_key = (t["year_yyyy"], t["month_yyyymm"], t["day_yyyymmdd"])

    if date_key not in date_lookup:
        pk_date = gen_key("DAT", counters["DateDim"])
        counters["DateDim"] += 1
        date_lookup[date_key] = pk_date

        DateDim.append([
            pk_date,
            t.get("year_yyyy"),  # es. "2021"
            t.get("month_yyyymm"),  # es. "202104"
            t.get("day_yyyymmdd"),  # es. "20210402"
            t.get("season", "")  # es. "Spring"
        ])
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

    # =====================================================
    # GROUPDIM — every song gets one GroupPK
    # =====================================================
    pk_group = gen_key("GRP", counters["GroupDim"])
    counters["GroupDim"] += 1
    GroupDim.append([pk_group])

    # =====================================================
    # GROUPFEATURES — one row per featured artist
    # =====================================================
    feats = [x.strip() for x in t.get("featured_artists", "").split(",")] if t.get("featured_artists") else []

    for f in feats:
        if not f:
            continue

        # Match featured artist name → ArtistCodePK
        matched_artist_pk = None
        for row in ArtistDim:
            if row[2].strip().lower() == f.lower():  # row[2] = Name
                matched_artist_pk = row[0]          # row[0] = ArtistCodePK
                #print("yuppieee")
                break

        if not matched_artist_pk:
            #print("grr")
            continue

        # Add row to GroupFeatures
        GroupFeatures.append([pk_group, matched_artist_pk])

    # =====================================================
    # FACT TABLE
    # =====================================================
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
        pk_group     # NEW foreign key
    ])

# ======================================================
# WRITE CSV FILES
# ======================================================
write_csv("AlbumDim.csv", ["AlbumCodePK","AlbumTitle","AlbumType", "AlbumReleaseDate"], AlbumDim)
write_csv("TextDim.csv", ["TextCodePK","N_Swear_Words_IT","N_Swear_Words_EN","Is_Explicit", "Lyrics"], TextDim)
write_csv("ArtistGeoDim.csv", ["ArtistGeoCodePK","H3_index","Country","Region","Province","City"], ArtistGeoDim)
write_csv("ArtistDim.csv", ["ArtistCodePK","ArtistGeoCodeFK","Name","Gender","Birth_date", 'Birth_place',"Nationality"], ArtistDim)
write_csv("DateDim.csv", ["DateCodePK","Year","Month","Day","Season"], DateDim)
write_csv("SymphonyDim.csv", ["SymphonyCodePK","BPM","Rolloff","Flux","RMS","Flatness","Spectral_Complexity","Pitch","Loudness"], SymphonyDim)
write_csv("GroupDim.csv", ["GroupPK"], GroupDim)
write_csv("GroupFeatures.csv", ["GroupFK","FeaturedArtistFK"], GroupFeatures)
write_csv("Published_Song_fact.csv",
          ["Track_ID","Title","Duration",
           "Streams_1month","Popularity","Category",
           "ArtistCodeFK","AlbumCodeFK","DateCodeFK","SymphonyCodeFK","TextCodeFK","GroupFK"],
          PublishedFact)

print("DONE! All warehouse tables generated")