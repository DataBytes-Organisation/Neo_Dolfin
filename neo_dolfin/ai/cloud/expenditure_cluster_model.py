import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


def expenditure_cluster_model(trans_data):
    cleaned_data = trans_data[['transactionDate', 'amount', 'description']]
    cleaned_data = cleaned_data[cleaned_data['amount'] < 0]
    cleaned_data['amount'] = cleaned_data['amount'] * -1

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
            if silhouette_avg <= best_score:
                break
            best_score = silhouette_avg
            best_k = k
            best_model = kmeans

        return best_k, best_model

    def convert_to_json_array(df):
        json_array = []
        for index, value in df.items():
            json_obj = {"value": value, "name": index}
            json_array.append(json_obj)
        return json_array

    k_auto, kmeans_auto = auto_kmeans(cleaned_data)
    kmeans_auto.fit(cleaned_data[['amount']])

    labels_auto = kmeans_auto.predict(cleaned_data[['amount']])

    centroids = kmeans_auto.cluster_centers_

    sorted_centroids = np.argsort(centroids.flatten())
    cluster_labels = [f'Level {i}' for i in range(k_auto)]

    label_mapping = {sorted_centroids[i]: cluster_labels[i] for i in range(len(cluster_labels))}

    expenditure_labels = np.array([label_mapping[label] for label in labels_auto])

    cleaned_data['Expenditure Level'] = expenditure_labels
    trans_data_with_level = cleaned_data.sort_values(by='Expenditure Level')
    trans_data_cluster = convert_to_json_array(trans_data_with_level.groupby('Expenditure Level')['amount'].sum())

    return trans_data_with_level, trans_data_cluster
