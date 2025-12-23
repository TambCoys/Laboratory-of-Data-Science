from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import seaborn as sns
import matplotlib.pyplot as plt


def k_means_choice(df, range_lower=2, range_upper=30, n_init=10, max_iter=100):
    """
    A function to test which choice of n_cluster (k) is best. It performs k-means from to in [range_lower, range_upper] and shows for each
    the Sum of Squared Error (SSE) and silhouette score.
    """
    sse_list = []
    sil_list = []
    
    for k in range(range_lower, range_upper):
        kmeans = KMeans(init='k-means++', n_clusters=k, n_init=n_init, max_iter=max_iter)
        kmeans.fit(df)
        sse_list.append(kmeans.inertia_)
        sil_list.append(silhouette_score(df, kmeans.labels_))
        
    fig, axs = plt.subplots(2) 

    sns.lineplot(x=range(2,len(sse_list)+2), y=sse_list, marker='o', ax=axs[0])
    axs[0].set(xlabel='k', ylabel='SSE')
    
    sns.lineplot(x=range(2,len(sil_list)+2), y=sil_list, marker='o', ax=axs[1])
    axs[1].set(xlabel='k', ylabel='Silhouette')
    

    plt.tight_layout() # Adjust the padding between and around subplots
