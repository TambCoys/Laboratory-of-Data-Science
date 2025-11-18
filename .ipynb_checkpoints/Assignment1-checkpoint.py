import json
import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np

# 1. Carica tracks.json
with open('tracks.json', encoding='utf-8') as f:
    tracks = json.load(f)
df_tracks = pd.DataFrame(tracks)

# 2. Carica artists.xml
tree = ET.parse('artists.xml')
root = tree.getroot()
artists = []
for row in root.findall('row'):
    artists.append({elem.tag: elem.text for elem in row})
df_artists = pd.DataFrame(artists)

a = df_tracks.isnull().sum()
b = (df_artists).isnull().sum()

print(a,b)

tr_desc = df_tracks.describe(include="all")
ar_desc = df_artists.describe(include="all")

print(tr_desc)
print(ar_desc)