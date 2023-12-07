import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd


def cluster(trans_data, preprocess=True):
    """
    Main model function for clustering expenditure data.
    It processes the data, applies KMeans clustering, and returns the clustered data along with cluster summaries.
    :param trans_data: DataFrame containing transaction data.
    :param preprocess: Boolean to indicate whether preprocessing should be applied.
    :return: Tuple of processed DataFrame with expenditure levels and JSON array with cluster summaries.
    """

    def preprocess_data(data):
        """
        Preprocesses the transaction data by filtering and transforming relevant columns.
        :param data: DataFrame containing raw transaction data.
        :return: DataFrame after preprocessing.
        """
        preprocessed_data = data[['transactionDate', 'amount', 'description']].copy()
        preprocessed_data = preprocessed_data[preprocessed_data['amount'] < 0]
        preprocessed_data['amount'] = preprocessed_data['amount'] * -1
        return preprocessed_data

    def auto_kmeans(data):
        """
        Preprocesses the transaction data by filtering and transforming relevant columns.
        :param data: DataFrame containing raw transaction data.
        :return: DataFrame after preprocessing.
        """
        k_range = range(3, 11)
        kmeans = KMeans(n_clusters=2, n_init='auto')
        kmeans.fit(data[['amount']])
        labels = kmeans.labels_
        best_score = silhouette_score(data[['amount']], labels)
        best_k = 2
        best_model = kmeans

        for k in k_range:
            kmeans = KMeans(n_clusters=k, n_init='auto')
            kmeans.fit(data[['amount']])
            labels = kmeans.labels_
            silhouette_avg = silhouette_score(data[['amount']], labels)
            if silhouette_avg <= best_score:
                break
            best_score = silhouette_avg
            best_k = k
            best_model = kmeans

        return best_k, best_model

    def convert_df_to_json_array(df):
        """
        Converts a DataFrame into a JSON array format for easier data visualization.
        :param df: DataFrame to convert.
        :return: JSON array representation of the DataFrame.
        """
        json_array = []
        for index, value in df.items():
            json_obj = {"value": value, "name": index}
            json_array.append(json_obj)
        return json_array

    cleaned_data = preprocess_data(trans_data) if preprocess else trans_data

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
    trans_data_cluster = convert_df_to_json_array(trans_data_with_level.groupby('Expenditure Level')['amount'].sum())

    return trans_data_with_level, trans_data_cluster
