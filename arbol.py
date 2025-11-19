import csv
import math
from collections import Counter
import graphviz
import sys
import io
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

def text_to_pdf(text, pdf):
    fig = plt.figure(figsize=(8.27, 11.69))
    plt.axis('off')
    plt.text(0.05, 0.95, text, va='top', ha='left', wrap=True, fontsize=8, family='monospace')
    pdf.savefig(fig)
    plt.close(fig)

def entropia(datos, idx_final):
    total = len(datos)
    if total == 0: return 0
    categorias = [fila[idx_final] for fila in datos]
    conteo = Counter(categorias)
    entropia_val = 0.0
    for cantidad in conteo.values():
        p = cantidad / total
        if p > 0: entropia_val -= p * math.log2(p)
    return entropia_val

def split(datos, idx_final, indices_vars):
    if not datos or not indices_vars: return None, -1
    entropia_global = entropia(datos, idx_final)
    n = len(datos)
    mejor_ganancia, mejor_col = -1, None
    for i in indices_vars:
        valores = set(f[i] for f in datos)
        entropia_media = sum(
            (len(sub := [f for f in datos if f[i] == v]) / n) * entropia(sub, idx_final)
            for v in valores
        )
        ganancia = entropia_global - entropia_media
        if ganancia > mejor_ganancia:
            mejor_ganancia, mejor_col = ganancia, i
    return mejor_col, mejor_ganancia

def categoria_mayoritaria(datos, idx_final):
    if not datos: return "SinDatos"
    return Counter(f[idx_final] for f in datos).most_common(1)[0][0]

def construir_arbol(datos, encabezado, indices_vars, idx_final):
    categorias_en_nodo = set(f[idx_final] for f in datos)
    if len(categorias_en_nodo) == 1: return list(categorias_en_nodo)[0]
    if not indices_vars: return categoria_mayoritaria(datos, idx_final)

    mejor_idx, mejor_ganancia = split(datos, idx_final, indices_vars)
    if mejor_idx is None or mejor_ganancia <= 0:
        return categoria_mayoritaria(datos, idx_final)

    nombre_var = encabezado[mejor_idx]
    nodo = {nombre_var: {}}
    nuevos_indices = [i for i in indices_vars if i != mejor_idx]
    for valor in set(f[mejor_idx] for f in datos):
        subconjunto = [f for f in datos if f[mejor_idx] == valor]
        nodo[nombre_var][valor] = construir_arbol(subconjunto, encabezado, nuevos_indices, idx_final)
    return nodo

def get_reglas_dec_text(arbol, regla_actual="Si", reglas_lista=None):
    if reglas_lista is None: reglas_lista = []
    if not isinstance(arbol, dict):
        regla_limpia = regla_actual.strip().rstrip("y").strip()
        reglas_lista.append(f"{regla_limpia} → Categoría = {arbol}")
        return reglas_lista

    var = list(arbol.keys())[0]
    for valor, subarbol in arbol[var].items():
        nueva = f"{regla_actual} {var} = '{valor}'" if regla_actual.strip() == "Si" else f"{regla_actual} y {var} = '{valor}'"
        get_reglas_dec_text(subarbol, nueva, reglas_lista)
    return reglas_lista

def cargar_csv(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8-sig') as f:
            # Read the first line to determine the delimiter
            header_line = f.readline()
            f.seek(0)  # Reset file pointer

            # Heuristic: Use semicolon if it's more frequent than comma
            if header_line.count(';') > header_line.count(','):
                delimiter = ';'
            else:
                delimiter = ','
            
            lector = csv.reader(f, delimiter=delimiter)
            header = next(lector)
            datos = [fila for fila in lector if fila and any(fila) and len(fila) == len(header)]
        return header, datos
    except (FileNotFoundError, Exception) as e:
        print(f"Error al cargar CSV: {e}", file=sys.stderr)
        return None, None

def dibujar_arbol_pdf(arbol, nombre_salida="arbol_decision_output.pdf"):
    dot = graphviz.Digraph(comment='Árbol de Decisión')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightgrey')
    
    def agregar_nodos(subarbol, padre=None, etiqueta=''):
        node_id = str(id(subarbol))
        if not isinstance(subarbol, dict):
            dot.node(node_id, subarbol, fillcolor='lightblue')
            if padre: dot.edge(padre, node_id, label=etiqueta)
            return
        var = list(subarbol.keys())[0]
        dot.node(node_id, var)
        if padre: dot.edge(padre, node_id, label=etiqueta)
        for val, sub in subarbol[var].items():
            agregar_nodos(sub, node_id, str(val))
    
    try:
        agregar_nodos(arbol)
        dot.render(nombre_salida.replace('.pdf', ''), format='pdf', cleanup=True, view=False)
        print(f"Gráfico del árbol guardado en '{nombre_salida.replace('.pdf', '.pdf')}'")
    except Exception as e:
        print(f"Error al generar el gráfico del árbol: {e}", file=sys.stderr)

def main():
    ruta_csv = input('Ingrese el nombre del archivo .CSV:\n')
    encabezado, datos = cargar_csv(ruta_csv)
    if not (encabezado and datos):
        print("No se pudieron cargar los datos. Abortando.")
        return

    try:
        nombre_categoria_final = input("Ingrese la columna objetivo de decisión: ")
        nombre_var_inicio = input('Ingrese la columna desde donde se va a tomar en cuenta: ')
        idx_final_int = encabezado.index(nombre_categoria_final)
        idx_inicio_int = encabezado.index(nombre_var_inicio)
        indices_vars = list(range(idx_inicio_int, idx_final_int))
    except ValueError:
        print("Nombre de columna no válido. Abortando.")
        return

    arbol = construir_arbol(datos, encabezado, indices_vars, idx_final_int)
    
    output_pdf_grafico = "arbol_decision_visual.pdf"
    dibujar_arbol_pdf(arbol, output_pdf_grafico)

    reglas_texto = "\n".join(get_reglas_dec_text(arbol))
    output_pdf_reglas = "arbol_decision_reglas.pdf"
    with PdfPages(output_pdf_reglas) as pdf:
        text_to_pdf("REGLAS DE DECISIÓN\n\n" + reglas_texto, pdf)
    print(f"Reglas de decisión guardadas en '{output_pdf_reglas}'")

if __name__ == '__main__':
    main()
