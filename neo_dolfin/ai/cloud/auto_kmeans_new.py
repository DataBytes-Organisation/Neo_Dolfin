import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def expenditure_cluster_model(trans_data):
    def auto_kmeans(data):
        k_range = range(2, 11)
        best_score = -1
        best_k = 2
        best_model = None

        for k in k_range:
            kmeans = KMeans(n_clusters=k, n_init=10)
            kmeans.fit(data[['amount']])
            labels = kmeans.labels_
            silhouette_avg = silhouette_score(data[['amount']], labels)
            if silhouette_avg > best_score:
                best_score = silhouette_avg
                best_k = k
                best_model = kmeans

        return best_k, best_model

    k_auto, kmeans_auto = auto_kmeans(trans_data)
    trans_data['cluster'] = kmeans_auto.predict(trans_data[['amount']])

    cluster_totals = trans_data.groupby('cluster')['amount'].sum().reset_index()
    cluster_totals['name'] = ['Level ' + str(i) for i in range(k_auto)]

    trans_data_with_level = trans_data.copy()
    trans_data_cluster = cluster_totals.to_dict('records')

    return trans_data_with_level, trans_data_cluster

trans_data = pd.read_csv("../../static/data/transaction_ut.csv")
trans_data['amount'] = trans_data['amount'].abs()

trans_data_with_level, trans_data_cluster = expenditure_cluster_model(trans_data)

print(trans_data_with_level.head())
print(trans_data_cluster)
