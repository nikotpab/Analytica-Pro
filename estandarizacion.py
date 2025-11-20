import pandas as pd
from sklearn.preprocessing import StandardScaler


def estandarizar_datos(ruta_csv, nombre_columna):
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        return f"Error al leer el archivo CSV: {e}"

    if nombre_columna not in df.columns:
        return f"Error: La columna '{nombre_columna}' no se encuentra en el archivo."

    try:
        scaler = StandardScaler()
        columna_datos = df[[nombre_columna]].values.astype(float)
        df[f'{nombre_columna}_z'] = scaler.fit_transform(columna_datos)

        # Devolver una muestra del DataFrame transformado y estadísticas clave
        output_df = df[[nombre_columna, f'{nombre_columna}_z']].head(10)

        output_str = f"--- Estandarización (Z-Score) ---\n"
        output_str += f"Media: {scaler.mean_[0]:.4f}\n"
        output_str += f"Desviación Estándar: {scaler.scale_[0]:.4f}\n\n"
        output_str += f"Muestra de Datos (Original vs. Estandarizado):\n{output_df.to_string(index=False)}"

        return output_str
    except ValueError:
        return f"Error: La columna '{nombre_columna}' no pudo ser convertida a valores numéricos."
    except Exception as e:
        return f"Ocurrió un error durante la estandarización: {e}"