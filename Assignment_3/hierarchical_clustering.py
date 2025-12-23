import numpy as np
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt

def get_linkage_matrix(model):
    # Create linkage matrix 
    
    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack(
        [model.children_, model.distances_, counts]
    ).astype(float)

    return linkage_matrix

def plot_dendrogram(model, **kwargs):
    linkage_matrix = get_linkage_matrix(model)
    dendrogram(linkage_matrix, **kwargs)

def hierarchical_clust(df, distance_threshold, n_clusters=None, metric='euclidean', linkage='complete'):
    """
    Functions to perform hierarchical clustering on a DataFrame and show the results.
    """
    model = AgglomerativeClustering(distance_threshold=distance_threshold,
                                n_clusters=n_clusters, metric=metric, linkage=linkage)
    model = model.fit(df)
    plt.title("Hierarchical Clustering Dendrogram - %s LINK" % (linkage))
    plot_dendrogram(model, truncate_mode="lastp", color_threshold=distance_threshold)
    plt.xlabel("Number of points in node (or index of point if no parenthesis).")

    plt.show()

