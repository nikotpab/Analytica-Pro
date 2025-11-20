from flask import Flask, request, jsonify
from flasgger import Swagger
import kmedias as kme
import kmodas as kmo
import arbol as tree
import chimerge as cm
import estandarizacion as est
import normalizacion as norm
import escala_log as log
import os

app = Flask("AnalyticaPro")

# ==================== EFS VOLUME INTEGRATION ====================
# Use mounted EFS volume for persistent data storage
DATA_VOLUME_PATH = "/app/data"  # This matches the containerPath in task definition

# Ensure data directory exists when app starts
os.makedirs(DATA_VOLUME_PATH, exist_ok=True)
print(f"EFS volume mounted at: {DATA_VOLUME_PATH}")  # For debugging
# ==================== END EFS VOLUME INTEGRATION ====================

app.config['SWAGGER'] = {
    'title': 'AnalyticaPro API',
    'uiversion': 3,
    "specs_route": "/algoritmos/"
}
swagger = Swagger(app)


@app.route('/')
def welcome():
    """A welcome message.
    ---
    responses:
      200:
        description: Returns a welcome message.
    """
    return 'Bienvenidx a AnalyticaPro'


@app.route('/algoritmos', methods=['POST'])
def run_algorithm():
    """
    Run a specified data analysis algorithm.
    ---
    tags:
      - Algorithms
    parameters:
      - name: body
        in: body
        required: true
        schema:
          id: AlgorithmRequest
          required:
            - algoritmo
            - data_path
          properties:
            algoritmo:
              type: string
              description: The algorithm to execute.
              enum: ['ESTANDARIZACION', 'NORMALIZACION', 'ESCALA_LOG', 'CHIMERGE', 'KMODAS', 'KMEDIAS', 'ARBOL']
            data_path:
              type: string
              description: Absolute path to the input CSV data file. Must be within /app/data/ directory.
            nombre_columna:
              type: string
              description: Name of the column to process (for ESTANDARIZACION, NORMALIZACION, ESCALA_LOG).
            objetivo:
              type: string
              description: Name of the target column (for ARBOL).
            inicio:
              type: string
              description: Name of the starting column for analysis range (for ARBOL).
    responses:
      200:
        description: Algorithm executed successfully. Returns path(s) to the output PDF(s).
      400:
        description: Bad request due to missing or invalid parameters.
      500:
        description: Internal server error during algorithm execution.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be in JSON format"}), 400

    req_data = request.get_json()
    algoritmo = req_data.get('algoritmo')
    data_path = req_data.get('data_path')

    if not all([algoritmo, data_path]):
        return jsonify({"error": "Missing required parameters: 'algoritmo' and 'data_path'"}), 400

    # ==================== SECURITY CHECK FOR EFS VOLUME ====================
    # Ensure data_path is within our mounted EFS volume for security
    if not data_path.startswith(DATA_VOLUME_PATH):
        return jsonify({
            "error": f"Data path must be within the EFS volume directory: {DATA_VOLUME_PATH}. Received: {data_path}"
        }), 400
    # ==================== END SECURITY CHECK ====================

    if not os.path.exists(data_path):
        return jsonify({"error": f"Data file not found at: {data_path}"}), 400

    output_filename = f"{os.path.splitext(os.path.basename(data_path))[0]}_{algoritmo.lower()}_output.pdf"
    output_path = os.path.join(os.path.dirname(data_path), output_filename)

    try:
        if algoritmo in ['ESTANDARIZACION', 'NORMALIZACION', 'ESCALA_LOG']:
            nombre_columna = req_data.get('nombre_columna')
            if not nombre_columna:
                return jsonify({"error": f"Missing 'nombre_columna' for {algoritmo}"}), 400

            if algoritmo == 'ESTANDARIZACION':
                est.estandarizar_datos(data_path, nombre_columna, output_pdf_path=output_path)
            elif algoritmo == 'NORMALIZACION':
                norm.normalizar_datos(data_path, nombre_columna, output_pdf_path=output_path)
            elif algoritmo == 'ESCALA_LOG':
                log.transformar_log(data_path, nombre_columna, output_pdf_path=output_path)

            return jsonify({"message": f"{algoritmo} executed successfully.", "output_path": output_path})

        elif algoritmo == 'CHIMERGE':
            cm.run_chimerge(data_path, output_pdf_path=output_path)
            return jsonify({"message": "CHIMERGE executed successfully.", "output_path": output_path})

        elif algoritmo == 'KMODAS':
            kmo.run_kmodas(data_path, output_pdf_path=output_path)
            return jsonify({"message": "KMODAS executed successfully.", "output_path": output_path})

        elif algoritmo == 'KMEDIAS':
            kme.run_kmedias(data_path, output_pdf_path=output_path)
            return jsonify({"message": "KMEDIAS executed successfully.", "output_path": output_path})

        elif algoritmo == 'ARBOL':
            objetivo = req_data.get('objetivo')
            inicio = req_data.get('inicio')
            if not all([objetivo, inicio]):
                return jsonify({"error": "Missing 'objetivo' or 'inicio' for ARBOL"}), 400

            encabezado, datos = tree.cargar_csv(data_path)
            if not encabezado or not datos:
                return jsonify({"error": "Failed to load data for ARBOL algorithm"}), 500

            idx_final_int = encabezado.index(objetivo)
            idx_inicio_int = encabezado.index(inicio)
            indices_vars = list(range(idx_inicio_int, idx_final_int))

            arbol_resultado = tree.construir_arbol(datos, encabezado, indices_vars, idx_final_int)

            output_pdf_grafico = output_path.replace('.pdf', '_visual.pdf')
            output_pdf_reglas = output_path.replace('.pdf', '_reglas.pdf')

            tree.dibujar_arbol_pdf(arbol_resultado, output_pdf_grafico)

            reglas_texto = "\n".join(tree.get_reglas_dec_text(arbol_resultado))
            with tree.PdfPages(output_pdf_reglas) as pdf:
                tree.text_to_pdf("REGLAS DE DECISIÓN\n\n" + reglas_texto, pdf)

            return jsonify({
                "message": "ARBOL execution complete.",
                "output_files": {
                    "visual": output_pdf_grafico,
                    "rules": output_pdf_reglas
                }
            })

        else:
            return jsonify({"error": f"Unknown algorithm: {algoritmo}"}), 400

    except Exception as e:
        return jsonify({"error": f"An error occurred during execution: {str(e)}"}), 500


# ==================== NEW ENDPOINT FOR FILE MANAGEMENT ====================
@app.route('/files/list', methods=['GET'])
def list_files():
    """
    List files in the EFS data directory.
    ---
    tags:
      - File Management
    responses:
      200:
        description: Returns list of files in the data directory.
      500:
        description: Error reading directory.
    """
    try:
        files = []
        for item in os.listdir(DATA_VOLUME_PATH):
            item_path = os.path.join(DATA_VOLUME_PATH, item)
            files.append({
                "name": item,
                "path": item_path,
                "is_file": os.path.isfile(item_path),
                "size": os.path.getsize(item_path) if os.path.isfile(item_path) else 0
            })
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": f"Error reading directory: {str(e)}"}), 500


@app.route('/files/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the EFS data directory.
    ---
    tags:
      - File Management
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The file to upload
    responses:
      200:
        description: File uploaded successfully.
      400:
        description: No file provided.
      500:
        description: Error uploading file.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        filename = file.filename
        file_path = os.path.join(DATA_VOLUME_PATH, filename)
        file.save(file_path)
        return jsonify({
            "message": "File uploaded successfully",
            "path": file_path,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": f"Error uploading file: {str(e)}"}), 500


# ==================== END NEW ENDPOINTS ====================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)  # Added host and port for container