import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import silhouette_score

df = pd.read_csv("../../static/data/transaction_ut.csv")
cleaned_data = df[['transactionDate', 'amount', 'description']]
cleaned_data = cleaned_data[cleaned_data['amount'] < 0]
cleaned_data['amount'] = cleaned_data['amount'] * -1


kmeans = KMeans(n_clusters=3, n_init='auto')
kmeans.fit(cleaned_data[['amount']])

labels = kmeans.predict(cleaned_data[['amount']])

centroids = kmeans.cluster_centers_

sorted_centroids = np.argsort(centroids.flatten())
cluster_labels = ['Low Expenditure', 'Medium Expenditure', 'High Expenditure']

label_mapping = {sorted_centroids[i]: cluster_labels[i] for i in range(len(cluster_labels))}

expenditure_labels = np.array([label_mapping[label] for label in labels])

cleaned_data['Expenditure Level'] = expenditure_labels
cleaned_data = cleaned_data.sort_values(by='Expenditure Level')
sum_by_expenditure = cleaned_data.groupby('Expenditure Level')['amount'].sum()/cleaned_data['amount'].sum()
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

inertia = []
silhouette_scores = []

K_range = range(1, 11)

for k in K_range:
    kmeans = KMeans(n_clusters=k, n_init='auto')
    kmeans.fit(cleaned_data[['amount']])
    inertia.append(kmeans.inertia_)

    if k > 1:
        labels = kmeans.labels_
        silhouette_avg = silhouette_score(cleaned_data[['amount']], labels)
        silhouette_scores.append(silhouette_avg)
        print("For k = {}: Silhouette Score: {}".format(k, silhouette_avg))

plt.plot(K_range[1:], silhouette_scores, 'bo-')
plt.title('Silhouette Scores For Different k')
plt.xlabel('Number of clusters')
plt.ylabel('Silhouette Score')
plt.show()

plt.plot(K_range, inertia, 'bo-')
plt.title('Elbow Method For Optimal k')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.show()

spending_data = pd.read_csv("../../static/data/spending_data.csv")
sum_by_category = spending_data.groupby('Categories')['Amount'].sum() / spending_data['Amount'].sum()

print(sum_by_category)
