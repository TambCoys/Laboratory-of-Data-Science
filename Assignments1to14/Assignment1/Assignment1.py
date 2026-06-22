# -*- coding: utf-8 -*-
import json
import xml.etree.ElementTree as ET

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



def load_tracks_json(path: str) -> pd.DataFrame:
    with open(path, encoding="utf-8") as f:
        tracks = json.load(f)
    return pd.DataFrame(tracks)


def load_artists_xml(path: str) -> pd.DataFrame:
    tree = ET.parse(path)
    root = tree.getroot()

    artists = []
    for row in root.findall("row"):
        artists.append({elem.tag: elem.text for elem in row})

    return pd.DataFrame(artists)


def main():
    # 1) Carichiamo i dati
    df_tracks = load_tracks_json("tracks.json")
    df_artists = load_artists_xml("artists.xml")

    # 2) Descrittive + duplicati
    print("Guardiamo le distribuzioni di tracks")
    print(df_tracks.describe(include="all"))

    print("Guardiamo le distribuzioni di artists")
    print(df_artists.describe(include="all"))

    print("Duplicati:")
    print("Duplicati df_tracks:", df_tracks.duplicated().sum())
    print("Duplicati df_artists:", df_artists.duplicated().sum())

    # 3) Missing values

    print("Null per colonna tracks")
    print(df_tracks.isnull().sum())

    print("Null per colonna artists")
    print(df_artists.isnull().sum())

    # Percentuali missing per colonna (tracks)
    missing_tracks = (df_tracks.isnull().mean() * 100).round(2)
    missing_tracks = missing_tracks[missing_tracks > 0].sort_values(ascending=False)

    print("% MISSING (tracks) > 0")
    print(missing_tracks)

    # Per artists: prima trasformo le stringhe vuote in NA
    df_artists = df_artists.copy()
    df_artists.replace("", pd.NA, inplace=True)

    missing_artists = (df_artists.isnull().mean() * 100).round(2)
    missing_artists = missing_artists[missing_artists > 0].sort_values(ascending=False)

    print("\n=== % MISSING (artists) > 0 ===")
    print(missing_artists)

    # 4) Istogramma artisti per regione
    if "region" in df_artists.columns:
        artists_per_region = (
            df_artists["region"]
            .dropna()  #
            .astype(str)
            .str.strip()
        )
        artists_per_region = artists_per_region[artists_per_region != ""] 

        artists_per_region = artists_per_region.value_counts()

        plt.figure()
        artists_per_region.plot(kind="bar")
        plt.xlabel("Regione")
        plt.ylabel("Numero di artisti")
        plt.title("Numero di artisti per regione")
        plt.tight_layout()
        plt.show()
    else:
        print("\n[WARN] Colonna 'region' non trovata in df_artists: salto il grafico.")


    # 5) Feature potenziali da aggiungere o dati da fillare

    # aggressiveness = loudness + bpm
    if {"loudness", "bpm"}.issubset(df_tracks.columns):
        df_tracks["aggressiveness"] = pd.to_numeric(df_tracks["loudness"], errors="coerce") + \
                                      pd.to_numeric(df_tracks["bpm"], errors="coerce")
    else:
        print("Errore: 'loudness' o 'bpm' mancano in df_tracks: salto 'aggressiveness'")

    # debut_age = active_start - birth_date (in anni)
    if {"active_start", "birth_date"}.issubset(df_artists.columns):
        debut = pd.to_datetime(df_artists["active_start"], errors="coerce") - \
                pd.to_datetime(df_artists["birth_date"], errors="coerce")

        df_artists["debut_age"] = debut.dt.days / 365.25
    else:
        print("\n[WARN] 'active_start' o 'birth_date' mancano in df_artists: salto 'debut_age'.")


    # 6) Analisi disc_number
    if "disc_number" in df_tracks.columns:
        n_unique_disc = df_tracks["disc_number"].nunique(dropna=True)
        print("Disc_Number")
        print("Numero valori unici disc_number:", n_unique_disc)

        perc_disc_1 = round((df_tracks["disc_number"] == 1).mean() * 100, 2)
        print("Percentuale disc_number == 1:", perc_disc_1, "%")
    else:
        print("Errore: Colonna 'disc_number' non trovata in df_tracks.")




if __name__ == "__main__":
    main()
