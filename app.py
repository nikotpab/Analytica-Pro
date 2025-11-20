from flask import Flask, request, jsonify
from flasgger import Swagger
from flask_cors import CORS
import os
import logging
from werkzeug.utils import secure_filename
import json

logging.basicConfig(level=logging.DEBUG)

try:
    import kmedias as kme
    import kmodas as kmo
    import arbol as tree
    import chimerge as cm
    import estandarizacion as est
    import normalizacion as norm
    import escala_log as log
except ImportError as e:
    logging.error(f"Error al importar módulos de algoritmos: {e}")

app = Flask("AnalyticaPro")
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['SWAGGER'] = {
    'title': 'AnalyticaPro API',
    'uiversion': 3,
    "specs_route": "/algoritmos/"
}
swagger = Swagger(app)


@app.route('/')
def welcome():
    return 'Bienvenidx a AnalyticaPro'


# La ruta /download se elimina ya que la salida no es un archivo

@app.route('/algoritmos', methods=['POST'])
def run_algorithm():
    if 'data_file' not in request.files:
        return jsonify({"error": "Falta el archivo 'data_file' en la solicitud."}), 400

    file = request.files['data_file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo."}), 400

    algoritmo = request.form.get('algoritmo')
    if not algoritmo:
        return jsonify({"error": "Falta el parámetro 'algoritmo'."}), 400

    input_filename = secure_filename(file.filename)
    data_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    file.save(data_path)

    result_data = None
    error_message = None

    try:
        if algoritmo in ['ESTANDARIZACION', 'NORMALIZACION', 'ESCALA_LOG']:
            nombre_columna = request.form.get('nombre_columna')
            if not nombre_columna:
                return jsonify({"error": f"Falta el parámetro 'nombre_columna' para {algoritmo}"}), 400

            if algoritmo == 'ESTANDARIZACION':
                result_data = est.estandarizar_datos(data_path, nombre_columna)
                if result_data is None: error_message = f"La columna '{nombre_columna}' no se encontró en el archivo o no es numérica."
            elif algoritmo == 'NORMALIZACION':
                result_data = norm.normalizar_datos(data_path, nombre_columna)
                if result_data is None: error_message = f"La columna '{nombre_columna}' no se encontró en el archivo o no es numérica."
            elif algoritmo == 'ESCALA_LOG':
                result_data = log.transformar_log(data_path, nombre_columna)
                if result_data is None: error_message = f"La columna '{nombre_columna}' no se encontró en el archivo o no es numérica."

        elif algoritmo == 'CHIMERGE':
            result_data = cm.run_chimerge(data_path)
            if result_data is None: error_message = "Error durante la ejecución de Chi-Merge. Verifique el formato del archivo y las columnas."

        elif algoritmo == 'KMODAS':
            result_data = kmo.run_kmodas(data_path)
            if result_data is None: error_message = "Error en K-Modas. Asegúrese de que la columna 'X2' exista y sea numérica."

        elif algoritmo == 'KMEDIAS':
            result_data = kme.run_kmedias(data_path)
            if result_data is None: error_message = "Error en K-Medias. Verifique las columnas 'longitude', 'latitude', y 'median_house_value'."

        elif algoritmo == 'ARBOL':
            objetivo = request.form.get('objetivo')
            inicio = request.form.get('inicio')
            if not all([objetivo, inicio]):
                return jsonify({"error": "Faltan los parámetros 'objetivo' o 'inicio' para ARBOL"}), 400

            encabezado_raw, datos = tree.cargar_csv(data_path)
            if not encabezado_raw or not datos:
                return jsonify({"error": "No se pudieron cargar los datos del CSV"}), 500

            encabezado = [h.strip() for h in encabezado_raw]

            if objetivo.strip() not in encabezado or inicio.strip() not in encabezado:
                error_msg = f"Las columnas '{objetivo}' o '{inicio}' no se encuentran en el archivo."
                return jsonify({"error": error_msg}), 400

            idx_final_int = encabezado.index(objetivo.strip())
            idx_inicio_int = encabezado.index(inicio.strip())
            indices_vars = list(range(idx_inicio_int, idx_final_int))

            arbol_resultado = tree.construir_arbol(datos, encabezado, indices_vars, idx_final_int)
            result_data = tree.get_reglas_dec_text(arbol_resultado)  # Obtener solo las reglas como lista de cadenas

        else:
            return jsonify({"error": f"Algoritmo desconocido: {algoritmo}"}), 400

        if result_data is None:
            return jsonify({"error": error_message or "La ejecución del algoritmo falló."}), 400

        # Si es una lista o un dict (como el arbol), lo convertimos a cadena para el frontend
        if isinstance(result_data, list):
            result_data_str = "\n".join(result_data)
        elif isinstance(result_data, dict):
            result_data_str = json.dumps(result_data, indent=2)
        else:
            result_data_str = str(result_data)

        return jsonify({
            "message": f"{algoritmo} ejecutado con éxito.",
            "resultado": result_data_str
        })

    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
    finally:
        # Opcional: limpiar el archivo de entrada después de procesar
        # os.remove(data_path)
        pass


if __name__ == '__main__':
    app.run(debug=True, port=5000)