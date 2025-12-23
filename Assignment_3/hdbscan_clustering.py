from sklearn.cluster import HDBSCAN
import seaborn as sns
import matplotlib.pyplot as plt

def hdbscan_clust(df, df_not_norm, x_axis, y_axis, cluster_selection_epsilon=0.5,
                  min_samples=5, min_cluster_size=10, max_cluster_size=15):
    """
    A function to perform HDBScan clustering on a DataFrame. The dataframe is assumed normalized. The non-normalized
    dataframe is used only to append the labels resulting from the clustering. x_axis and y_axis are used for the scatter
    plot and need to be attributes of the non-normalized dataframe. The other inputs are connected to the clustering.
    """
    hdb = HDBSCAN(cluster_selection_epsilon=cluster_selection_epsilon, min_samples=min_samples, 
                  min_cluster_size=min_cluster_size, max_cluster_size=max_cluster_size,
                  store_centers="centroid")
    hdb.fit(df)
    df_not_norm['hdbscan_labels'] = hdb.labels_
    sns.scatterplot(data=df_not_norm, 
                    x=x_axis,
                    y=y_axis, 
                    hue=hdb.labels_, 
                    style=hdb.labels_, 
                    palette="bright")
    

    plt.show()

