from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

def k_means_clust(df, df_not_norm, n_clust, n_init=20, max_iter=100, random_state=42, legend=False, hue='primary_artist'):
    """
    A function to perform K-means clustering on a DataFrame. The dataframe is assumed normalized. The non-normalized
    dataframe is used only to append the labels resulting from the clustering. The other inputs are connected to the clustering.
    The function also shows a countplot showing for each cluster how many element of a certain hue are there. For example,
    for the default hue='primary_artist', the countplot shows in each cluster how many songs of each artist there are.
    """
    kmeans = KMeans(n_clusters=n_clust, n_init=n_init, max_iter=max_iter, random_state=random_state)
    kmeans.fit(df)
    df_not_norm['kmeans_labels'] = kmeans.labels_
    fig = plt.figure(figsize=(13, 8))
    sns.countplot(data=df_not_norm, x='kmeans_labels', hue=hue, legend=False)

    plt.show()
