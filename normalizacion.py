import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def normalizar_datos(ruta_csv, nombre_columna):
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        return f"Error al leer el archivo CSV: {e}"

    if nombre_columna not in df.columns:
        return f"Error: La columna '{nombre_columna}' no se encuentra en el archivo."

    try:
        scaler = MinMaxScaler()
        columna_datos = df[[nombre_columna]].values.astype(float)
        df[f'{nombre_columna}_norm'] = scaler.fit_transform(columna_datos)

        # Devolver una muestra del DataFrame transformado y estadísticas clave
        output_df = df[[nombre_columna, f'{nombre_columna}_norm']].head(10)

        # Obtener Min y Max usados para la normalización
        data_min = scaler.data_min_[0]
        data_max = scaler.data_max_[0]

        output_str = f"--- Normalización (Min-Max) ---\n"
        output_str += f"Valor Mínimo Original: {data_min:.4f}\n"
        output_str += f"Valor Máximo Original: {data_max:.4f}\n\n"
        output_str += f"Muestra de Datos (Original vs. Normalizado [0-1]):\n{output_df.to_string(index=False)}"

        return output_str
    except ValueError:
        return f"Error: La columna '{nombre_columna}' no pudo ser convertida a valores numéricos."
    except Exception as e:
        return f"Ocurrió un error durante la normalización: {e}"