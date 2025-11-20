import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import json


def run_kmedias(file_path):
    try:
        home_data = pd.read_csv(file_path, usecols=['longitude', 'latitude', 'median_house_value'])
        home_data.dropna(inplace=True)
    except Exception as e:
        return f"Error en K-Medias: {e}"

    if home_data.empty:
        return "Error: Datos insuficientes después de la limpieza."

    X_train, _, y_train, _ = train_test_split(
        home_data[['latitude', 'longitude']],
        home_data[['median_house_value']],
        test_size=0.33,
        random_state=0
    )
    X_train_norm = preprocessing.normalize(X_train)

    K = range(2, 8)
    scores = []

    # Calcular la puntuación de silueta para encontrar el mejor K
    for k in K:
        try:
            model = KMeans(n_clusters=k, random_state=0, n_init='auto', max_iter=300).fit(X_train_norm)
            score = silhouette_score(X_train_norm, model.labels_, metric='euclidean')
            scores.append((k, score))
        except Exception:
            scores.append((k, -1))  # Error en clustering

    best_k, best_score = max(scores, key=lambda item: item[1]) if scores and max(scores, key=lambda item: item[1])[
        1] > 0 else (3, 0)

    # Ejecutar KMeans con el mejor K o un valor predeterminado (k=3)
    final_k = 3 if best_k == 0 else best_k
    kmeans_final = KMeans(n_clusters=final_k, random_state=0, n_init='auto', max_iter=300).fit(X_train_norm)

    # Agregar clusters al dataset original para el resumen
    X_train['cluster'] = kmeans_final.labels_
    y_train['cluster'] = kmeans_final.labels_

    # Resumen de valores de vivienda por cluster
    cluster_summary = y_train.groupby('cluster')['median_house_value'].agg(['count', 'mean', 'std']).reset_index()

    output_dict = {
        "algoritmo": "K-Medias",
        "mejor_k_encontrado": int(final_k),
        "puntuacion_silueta_maxima": f"{best_score:.4f}",
        "centroides": [c.tolist() for c in kmeans_final.cluster_centers_],
        "resumen_cluster_valor_vivienda": cluster_summary.to_dict(orient='records')
    }

    return json.dumps(output_dict, indent=2)