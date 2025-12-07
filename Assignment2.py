# ASSIGNMENT 2 â€“ DATA CLEANING FINALE (NO PANDAS)

import json
import xml.etree.ElementTree as ET
import requests
import time
from statistics import median, mode, StatisticsError
from datetime import datetime
import h3

# ==========================
# 1) GEOCODING ARTISTI
# ==========================

# Dizionario di partenza: Artista e provincia di nascita
artists_birth_province = {
    "alfa": "Genova",
    "anna pepe": "La Spezia",
    "beba": "Torino",
    "bigmama": "Avellino",
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
    "yendry": "Santo Domingo, Dominican Republic",
    "99 posse": "Napoli",
    "articolo 31": "Milano",
    "bushwaka": "La Spezia",
    "club dogo": "Milano",
    "colle der fomento": "Roma",
    "cor veleno": "Roma",
    "dark polo gang": "Roma",
    "doll kill": "Cagliari",
    "joey funboy": "Bolzano",
    "mike24": "Avellino",
    "miss simpatia": "Ancona",
    "sottotono": "Novara",
    "yeиdry": "Santo Domingo, Dominican Republic",
    "nesli": "Ancona",
    "fabri fibra": "Ancona",
    "shablo": "Buenos Aires, Argentina",
    "baby k": "Singapore"
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


# 2) Costruzione artists_geo (Artista e info geografiche)
artists_geo = {}

for artist, birthplace in artists_birth_province.items():
    info = geocode_place(birthplace)
    artists_geo[artist] = info

print("\n=Valori Aggiunti=\n")
for artist, info in artists_geo.items():
    print(f"{artist}: {info}")

# Forzo manualmente la regione per baby k
if artists_geo.get("baby k") is not None:
    artists_geo["baby k"]["region"] = "Singapore"




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

    # 3) scrivo solo se il campo Ã¨ vuoto / "None" / "null" / "nan"
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
    print(f"AGGIORNATO’ {name_xml}")

for row in root.findall('row'):
    lat = float(row.find("latitude").text)
    long = float(row.find("longitude").text)
    h3_index = h3.latlng_to_cell(lat, long, res=5)
    # res=4 -> circa 897 km^2, res=5 -> circa 128 km^2, res=6 -> circa 18 km^2
    new_elem_h3 = ET.SubElement(row, "h3_idx")
    new_elem_h3.text = h3_index
    fields_added += 1

#Convertiamo le date in un formato più comodo
date_cat = ["birth_date", "active_start", "active_end"]

for row in root.findall('row'):
    for field in date_cat:
        elem = row.find(field)
        if elem is None or elem.text is None:
            continue

        original = elem.text.strip()

        # tentiamo di convertire YYYY-MM-DD in YYYYMMDD
        try:
            dt = datetime.strptime(original, "%Y-%m-%d")
            elem.text = dt.strftime("%Y%m%d")  # nuovo formato
        except Exception:
            continue

# Salva XML pulito con geo dati
tree.write("artists_cleaned.xml", encoding="utf-8", xml_declaration=True)
print(f"\nArtisti aggiornati con geocoding: {updated_artists}")
print(f"Campi aggiunti totali: {fields_added}")
print("â†’ artists_cleaned.xml generato e pronto per Assignment 4!\n")


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

# =========================================================
# FIX MISSING DATES (0 or Null)
# =========================================================

# 1. Calculate Medians (from songs that have valid dates)
# We collect valid values to compute the median statistics
valid_years = [t['year'] for t in tracks if t.get('year') and t['year'] != 0]
valid_months = [t['month'] for t in tracks if t.get('month') and t['month'] != 0]
valid_days = [t['day'] for t in tracks if t.get('day') and t['day'] != 0]

# Use statistics.median (imported in your script)
med_year = int(median(valid_years)) if valid_years else 2020
med_month = int(median(valid_months)) if valid_months else 1
med_day = int(median(valid_days)) if valid_days else 1

# 2. Apply the Logic
for track in tracks:
    # Check if the song date is invalid (0 or None)
    if track.get('year') == 0 or track.get('year') is None:
        
        alb_date = track.get('album_release_date')
        
        # Check if Album Date exists and is not empty
        if alb_date and len(str(alb_date)) >= 4:
            try:
                # album_release_date is typically "YYYY-MM-DD" or "YYYY"
                parts = str(alb_date).split('-')
                
                # Set Year
                track['year'] = int(parts[0])
                
                # Set Month (use median if album date only has year)
                track['month'] = int(parts[1]) if len(parts) > 1 else med_month
                
                # Set Day (use median if album date is YYYY-MM)
                track['day'] = int(parts[2]) if len(parts) > 2 else med_day
                
            except (ValueError, IndexError):
                # If parsing fails, default to median
                track['year'] = med_year
                track['month'] = med_month
                track['day'] = med_day
        else:
            # Album date is missing or 0 -> Use Median
            track['year'] = med_year
            track['month'] = med_month
            track['day'] = med_day



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
    # Numerici â†’ mediana
    for field in numeric_fields:
        val = track.get(field)
        if val is None or str(val).strip() in ("", "null", "nan"):
            track[field] = medians[field]

    # Categorici â†’ moda
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

    month = track.get("month")
    day = track.get("day")

    season = None

    try:
        month = int(month)
        day = int(day)

        if (month == 12 and day >= 21) or month in (1, 2) or (month == 3 and day <= 19):
            season = "Winter"
        elif (month == 3 and day >= 20) or month in (4, 5) or (month == 6 and day <= 20):
            season = "Spring"
        elif (month == 6 and day >= 21) or month in (7, 8) or (month == 9 and day <= 22):
            season = "Summer"
        elif (month == 9 and day >= 23) or month in (10, 11) or (month == 12 and day <= 20):
            season = "Autumn"

    except:
        season = None

    track["season"] = season

#rendiamo più comode le variabili temporali
try:
    y = int(track.get("year"))
    m = int(track.get("month"))
    d = int(track.get("day"))

    # yyyy
    track["year_yyyy"] = f"{y:04d}"

    # yyyymm
    track["month_yyyymm"] = f"{y:04d}{m:02d}"

    # yyyymmdd
    track["day_yyyymmdd"] = f"{y:04d}{m:02d}{d:02d}"

except:
    # Se year/month/day sono mancanti
    track["year_yyyy"] = None
    track["month_yyyymm"] = None
    track["day_yyyymmdd"] = None

# -------- 2.4 Salvataggio --------
with open('tracks_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(tracks, f, indent=2, ensure_ascii=False)


print("Pulizia tracks.json completata. File: output2_tracks.json")