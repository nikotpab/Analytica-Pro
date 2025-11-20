import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
import json


def run_kmodas(file_path):
    try:
        dataset = pd.read_csv(file_path)
        X = dataset[['X2']].values.astype(float)
    except Exception as e:
        return f"Error en K-Modas: {e}"

    if X.size == 0:
        return "Error: Columna 'X2' vacía o no encontrada."

    # Se mantiene k=3 como valor predeterminado (basado en tu código original)
    try:
        kmeans = KMeans(n_clusters=3, init='k-means++', max_iter=300, n_init='auto', random_state=0)
        dataset['Cluster_X2'] = kmeans.fit_predict(X)

        centroides = kmeans.cluster_centers_.flatten().tolist()

        # Contar cuántos elementos hay en cada cluster
        conteo_clusters = dataset['Cluster_X2'].value_counts().sort_index().to_dict()

        output_dict = {
            "algoritmo": "K-Modas (Usando K-Means en X2)",
            "clusters_usados": 3,
            "centroides": centroides,
            "elementos_por_cluster": conteo_clusters,
            "muestra_datos_clusterizados": dataset[['X2', 'Cluster_X2']].head(10).to_dict(orient='records')
        }

        return json.dumps(output_dict, indent=2)
    except Exception as e:
        return f"Ocurrió un error durante la ejecución de K-Modas: {e}"