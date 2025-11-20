import pandas as pd
import numpy as np


def transformar_log(ruta_csv, nombre_columna):
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        return f"Error al leer el archivo CSV: {e}"

    if nombre_columna not in df.columns:
        return f"Error: La columna '{nombre_columna}' no se encuentra en el archivo."

    try:
        columna_datos = df[nombre_columna].astype(float)

        # Validación: log1p requiere valores >= -1, pero para transformación logarítmica es mejor > 0
        if (columna_datos < 0).any():
            return f"Error: La columna '{nombre_columna}' contiene valores negativos. No se recomienda la transformación logarítmica directa."

        df[f'{nombre_columna}_log'] = np.log1p(columna_datos)

        # Devolver una muestra del DataFrame transformado y estadísticas clave
        output_df = df[[nombre_columna, f'{nombre_columna}_log']].head(10)

        output_str = f"--- Transformación Logarítmica (np.log1p) ---\n"
        output_str += f"Estadísticas de '{nombre_columna}':\n{columna_datos.describe().to_string()}\n\n"
        output_str += f"Muestra de Datos (Original vs. Log):\n{output_df.to_string(index=False)}"

        return output_str
    except ValueError:
        return f"Error: La columna '{nombre_columna}' no pudo ser convertida a valores numéricos."
    except Exception as e:
        return f"Ocurrió un error durante la transformación: {e}"