import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import silhouette_score

df = pd.read_csv("../../static/data/transaction_ut.csv")
cleaned_data = df[['transactionDate', 'amount', 'description']]
cleaned_data = cleaned_data[cleaned_data['amount'] < 0]
cleaned_data['amount'] = cleaned_data['amount'] * -1


def auto_kmeans(data):
    k_range = range(2, 11)
    kmeans = KMeans(n_clusters=2, n_init=10)
    kmeans.fit(data[['amount']])
    labels = kmeans.labels_
    prev_score = silhouette_score(data[['amount']], labels)
    best_score = prev_score
    best_model = kmeans

    for k in k_range[1:]:
        kmeans = KMeans(n_clusters=k, n_init=10)
        kmeans.fit(data[['amount']])
        labels = kmeans.labels_
        silhouette_avg = silhouette_score(data[['amount']], labels)
        if silhouette_avg > best_score:
            best_score = silhouette_avg
            best_k = k
            best_model = kmeans

    return best_k, best_model


k_auto, kmeans_auto = auto_kmeans(cleaned_data)
kmeans_auto.fit(cleaned_data[['amount']])

labels_auto = kmeans_auto.predict(cleaned_data[['amount']])

centroids = kmeans_auto.cluster_centers_

sorted_centroids = np.argsort(centroids.flatten())
cluster_labels = [f'Level {i}' for i in range(k_auto)]

label_mapping = {sorted_centroids[i]: cluster_labels[i] for i in range(len(cluster_labels))}

expenditure_labels = np.array([label_mapping[label] for label in labels_auto])

cleaned_data['Expenditure Level'] = expenditure_labels
cleaned_data = cleaned_data.sort_values(by='Expenditure Level')
sum_by_expenditure = cleaned_data.groupby('Expenditure Level')['amount'].sum() / cleaned_data['amount'].sum()
print(sum_by_expenditure)
cleaned_file_path = '../../static/data/cloud.csv'
cleaned_data.to_csv(cleaned_file_path, index=False)

for i, expenditure_label in enumerate(cluster_labels):
    cluster_data = cleaned_data[cleaned_data['Expenditure Level'] == expenditure_label]
    plt.scatter(cluster_data['amount'], np.zeros_like(cluster_data['amount']), label=expenditure_label)

plt.scatter(centroids, np.zeros_like(centroids), c='red', s=100, marker='x', label='Centroids')

plt.title('Spending Structure with Expenditure Levels')
plt.xlabel('Expenditure')
plt.yticks([])
plt.legend()
plt.show()
