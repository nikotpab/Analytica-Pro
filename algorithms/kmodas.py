import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans


data = {
    "X0": ["A","C","B","A","A","C","A","B","C","B","B","C"],
    "X1": ["ARBOL","COPA","BUS","ARBOL","COPA","COPA","ARBOL","BUS","COPA","BUS","BUS","COPA"],
    "X2": [5,2,3,7,9,2,2,6,2,1,11,12]
}
dataset = pd.DataFrame(data)

X = dataset[['X2']].values

wcss = []
for i in range(1, 11):
    kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
    kmeans.fit(X)
    wcss.append(kmeans.inertia_)

plt.plot(range(1, 11), wcss, marker='o')
plt.title('Método del Codo')
plt.xlabel('Número de clusters')
plt.ylabel('WCSS')
plt.show()

kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=300, n_init=10, random_state=0)
dataset['Cluster_X2'] = kmeans.fit_predict(X)


print("Centroides:", kmeans.cluster_centers_.flatten())
print(dataset)

plt.scatter(X[dataset['Cluster_X2'] == 0], [0]*len(X[dataset['Cluster_X2'] == 0]), color='red', label='Cluster 1')
plt.scatter(X[dataset['Cluster_X2'] == 1], [0]*len(X[dataset['Cluster_X2'] == 1]), color='blue', label='Cluster 2')
plt.scatter(X[dataset['Cluster_X2'] == 2], [0]*len(X[dataset['Cluster_X2'] == 2]), color='green', label='Cluster 3')
plt.scatter(kmeans.cluster_centers_, [0]*3, s=200, c='yellow', label='Centroides')
plt.title('Clusters según X2')
plt.xlabel('Valor de X2')
plt.legend()
plt.show()