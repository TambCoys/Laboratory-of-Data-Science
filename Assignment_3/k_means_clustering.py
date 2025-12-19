# -*- coding: utf-8 -*-
"""
Created on Fri Dec 19 19:07:46 2025

@author: Utente
"""

from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def k_means_clust(df, df_not_norm, n_clust, n_init=20, max_iter=100, random_state=42, legend=False, hue='primary_artist'):
    kmeans = KMeans(n_clusters=n_clust, n_init=n_init, max_iter=max_iter, random_state=random_state)
    kmeans.fit(df)
    df_not_norm['kmeans_labels'] = kmeans.labels_
    fig = plt.figure(figsize=(13, 8))
    sns.countplot(data=df_not_norm, x='kmeans_labels', hue=hue, legend=False)
    plt.show()