# -*- coding: utf-8 -*-
"""
Created on Fri Dec 19 18:36:57 2025

@author: Utente
"""

import json
import pandas as pd
from sklearn.preprocessing import StandardScaler
import hierarchical_clustering as hc
import hdbscan_clustering as hdbc
import k_means_choice as km_choice
import k_means_clustering as kmc

# 1. Upload tracks.json
with open('tracks_cleaned.json', encoding='utf-8') as f:
    tracks = json.load(f)
df_tracks = pd.DataFrame(tracks)

to_keep = ['bpm', 'rolloff', 'flux', 'rms', 'flatness', 'spectral_complexity', 'pitch', 'loudness']
scaler = StandardScaler()
scaler.fit(df_tracks[to_keep])
df_norm = scaler.transform(df_tracks[to_keep])

hc.hierarchical_clust(df=df_norm, distance_threshold=10)

hdbc.hdbscan_clust(df=df_norm, df_not_norm=df_tracks, x_axis="pitch", y_axis="loudness",
                  cluster_selection_epsilon=0.5, min_samples=5)

df_tracks = df_tracks.drop(['hdbscan_labels'], axis=1)

km_choice.k_means_choice(df=df_norm, range_lower=2, range_upper=30)

n_clust = 7

kmc.k_means_clust(df=df_norm, df_not_norm=df_tracks, n_clust=n_clust)

label_to_cat = {0:'Minimal', 1:'Fast-Flow', 2:'Hype', 3:'Warm Bangers', 4:'Clean',
                5:'Melodic', 6:'Slow Dark'}

for i in range(n_clust):
    df = df_tracks.loc[df_tracks['kmeans_labels']==i, 'category'] = label_to_cat[i]
    

df_tracks_json = df_tracks.to_dict(orient='records')

with open('tracks_cleaned.json', 'w', encoding='utf-8') as f:

    json.dump(df_tracks_json, f, indent=2, ensure_ascii=False)
