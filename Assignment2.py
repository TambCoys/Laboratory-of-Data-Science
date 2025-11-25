# ASSIGNMENT 2 – DATA CLEANING FINALE (NO PANDAS)

import json
import xml.etree.ElementTree as ET
import requests
import time
from statistics import median, mode, StatisticsError
from datetime import datetime

# ==========================
# 1) GEOCODING ARTISTI
# ==========================

# Dizionario di partenza: ARTISTA → provincia di nascita
artists_birth_province = {
    "alfa": "Genova",
    "anna pepe": "La Spezia",
    "beba": "Torino",
    "big mama": "Avellino",
    "brusco": "Roma",
    "caneda": "Milano",
    "dargen d_amico": "Milano",
    "eva rea": "Catania",
    "guè pequeno": "Milano",
    "hindaco": "Enna",
    "johnny marsiglia": "Palermo",
    "miss keta": "Milano",
    "mistico": "Milano",
    "nerone": "Milano",
    "o zulù": "Napoli",
    "priestess": "Bari",
    "samuel heron": "La Spezia",
    "shiva": "Milano",
    "skioffi": "Frosinone",
    "yendry": "Santo Domingo, Dominican Republic"
}

# Cache per non ripetere le stesse chiamate al geocoder
CACHE = {}


def geocode_place(place):
    """
    Usa Nominatim per ottenere:
    - latitudine
    - longitudine
    - regione (state)
    - country
    - nationality (italiana / altro)
    """
    place = place.strip()
    if place in CACHE:
        return CACHE[place]

    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": place,
        "format": "json",
        "limit": 1,
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "DSS-Project-Unipi/1.0 (m.tamberi2@studenti.unipi.it)"
    }

    print(f"Geocoding: {place} ... ", end="", flush=True)
    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                first = data[0]
                lat = float(first["lat"])
                lon = float(first["lon"])
                addr = first.get("address", {})
                country = addr.get("country", "")
                region = addr.get("state", "")

                # stima della nazionalità (case-insensitive)
                country_lower = country.lower()
                if "italia" in country_lower or "italy" in country_lower:
                    nationality = "Italia"
                else:
                    nationality = None

                result = {
                    "province": place,
                    "region": region if region else None,
                    "country": country if country else None,
                    "nationality": nationality,
                    "latitude": lat,
                    "longitude": lon
                }
                CACHE[place] = result
                print("OK")
                # piccola pausa per non stressare il server
                time.sleep(1)
                return result
    except Exception as e:
        print(f"FAILED ({e})")

    CACHE[place] = None
    print("FAILED")
    time.sleep(1)
    return None


# 2) Costruzione artists_geo (ARTISTA → info geografiche)
artists_geo = {}

for artist, birthplace in artists_birth_province.items():
    info = geocode_place(birthplace)
    artists_geo[artist] = info

print("\n=Valori Aggiunti=\n")
for artist, info in artists_geo.items():
    print(f"{artist}: {info}")



def is_empty_text(text):
    """Riconosce come 'vuoto' None, '', 'None', 'null', 'nan'."""
    if text is None:
        return True
    t = text.strip()
    return t == "" or t.lower() in ("none", "null", "nan")

# Carica artists.xml
tree = ET.parse('artists.xml')
root = tree.getroot()

updated_artists = 0
fields_added = 0

for row in root.findall('row'):
    name_elem = row.find('name')
    if name_elem is None or not name_elem.text:
        continue

    name_xml = name_elem.text.strip()
    key_xml = name_xml.lower()

    # 1) ricavo la chiave da usare nel dizionario
    dict_name = key_xml

    if dict_name not in artists_birth_province:
        # nessuna info di nascita/geocoding per questo artista
        continue

    geo_info = artists_geo.get(dict_name)
    if not geo_info:
        continue

    # 2) preparo i valori da scrivere
    tags = {
        "birth_place": geo_info["province"],      # usiamo la provincia come luogo di nascita
        "province": geo_info["province"],
        "region": geo_info["region"],
        "country": geo_info["country"],
        "nationality": geo_info["nationality"],
        "latitude": str(geo_info["latitude"]),
        "longitude": str(geo_info["longitude"]),
    }

    # 3) scrivo solo se il campo è vuoto / "None" / "null" / "nan"
    for tag, value in tags.items():
        if value is None:
            continue
        elem = row.find(tag)
        if elem is None:
            elem = ET.SubElement(row, tag)
            fields_added += 1
        if is_empty_text(elem.text):
            elem.text = value
            fields_added += 1

    updated_artists += 1
    print(f"AGGIORNATO → {name_xml}")

# Salva XML pulito con geo dati
tree.write("artists_cleaned.xml", encoding="utf-8", xml_declaration=True)
print(f"\nArtisti aggiornati con geocoding: {updated_artists}")
print(f"Campi aggiunti totali: {fields_added}")
print("→ artists_cleaned.xml generato e pronto per Assignment 4!\n")


# ==========================
# 2) PULIZIA TRACKS.JSON
# ==========================

print("2. Pulizia tracks.json...")

with open('tracks.json', 'r', encoding='utf-8') as f:
    tracks = json.load(f)

stats_tracks = {
    "date_riempite": 0,
    "album_riempiti": 0,
}

# Campi numerici da riempire con mediana
numeric_fields = [
    "duration_ms",
    "popularity",
    "char_per_tok",
    "n_tokens",
    "n_sentences",
    "avg_token_per_clause",
    "flatness",
    "loudness",
    "pitch",
    "spectral_complexity",
    "rms",
    "flux",
    "rolloff",
    "bpm"
]

# Campi categorici da riempire con la moda
categorical_fields = ["disc_number", "track_number", "language"]


# -------- 2.1 Calcolo mediane per i campi numerici --------
medians = {}
for field in numeric_fields:
    vals = []
    for t in tracks:
        val = t.get(field)
        if val is None:
            continue
        s = str(val).strip()
        if s in ("", "null", "nan"):
            continue
        try:
            vals.append(float(s))
        except (ValueError, TypeError):
            continue
    medians[field] = median(vals) if vals else 0


# -------- 2.2 Calcolo mode per i campi categorici --------
def safe_mode(values):
    cleaned = [v for v in values if v not in (None, "", "null", "nan")]
    if not cleaned:
        return None
    try:
        return mode(cleaned)
    except StatisticsError:
        return cleaned[0]


modes = {}
for field in categorical_fields:
    vals = [t.get(field) for t in tracks]
    modes[field] = safe_mode(vals)


# -------- 2.3 Pulizia riga per riga --------
for track in tracks:
    # Numerici → mediana
    for field in numeric_fields:
        val = track.get(field)
        if val is None or str(val).strip() in ("", "null", "nan"):
            track[field] = medians[field]

    # Categorici → moda
    for field in categorical_fields:
        if modes[field] is None:
            continue
        val = track.get(field)
        if val is None or str(val).strip() in ("", "null", "nan"):
            track[field] = modes[field]

    # Date derivate da album_release_date
    if track.get("album_release_date"):
        try:
            base_date = track["album_release_date"].split("T")[0]
            dt = datetime.strptime(base_date, "%Y-%m-%d")
            if not track.get("year"):
                track["year"] = dt.year
                stats_tracks["date_riempite"] += 1
            if not track.get("month"):
                track["month"] = dt.month
                stats_tracks["date_riempite"] += 1
            if not track.get("day"):
                track["day"] = dt.day
                stats_tracks["date_riempite"] += 1
        except Exception:
            pass

    # Album da album_name
    if not track.get("album") and track.get("album_name"):
        track["album"] = track["album_name"]
        stats_tracks["album_riempiti"] += 1

    # explicit da swear_IT e swear_EN
    swear_it = track.get("swear_IT", 0)
    swear_en = track.get("swear_EN", 0)

    try:
        swear_it = int(swear_it)
    except (ValueError, TypeError):
        swear_it = 0
    try:
        swear_en = int(swear_en)
    except (ValueError, TypeError):
        swear_en = 0

    # False se entrambe 0, True altrimenti
    new_explicit = not (swear_it == 0 and swear_en == 0)
    track["explicit"] = new_explicit


# -------- 2.4 Salvataggio --------
with open('tracks_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(tracks, f, indent=2, ensure_ascii=False)
import pandas as pd


df_artists = pd.read_xml("artists_cleaned.xml", parser="etree")

print("\n== ANY ==")
print(df_artists.isnull().any())

print("\n== SUM ==")
print(df_artists.isnull().sum())

print("\n== PERCENT ==")
missing_pct_tracks = df_artists.isnull().mean() * 100
print(missing_pct_tracks)


print("Pulizia tracks.json completata. File: output2_tracks.json")
