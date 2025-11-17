import csv
import math
from collections import Counter
import graphviz

def entropia(datos, idx_final):
    total = len(datos)
    if total == 0:
        return 0
    entropia = 0.0
    categorias = [fila[idx_final] for fila in datos]
    conteo = Counter(categorias)
    for cat, cantidad in conteo.items():
        p = cantidad / total
        if p > 0:
            entropia -= p * math.log2(p)
    return entropia


def split(datos, encabezado, indices_vars, idx_final):
    entropia_global = entropia(datos, idx_final)
    n = len(datos)
    mejor_ganancia = -9999
    mejor_col = None
    for i in indices_vars:
        valores = set(f[i] for f in datos)
        entropia_media = 0
        for val in valores:
            subconjunto = [fila for fila in datos if fila[i] == val]
            peso = len(subconjunto) / n
            entropia_media += peso * entropia(subconjunto, idx_final)
        ganancia = entropia_global - entropia_media
        if ganancia > mejor_ganancia:
            mejor_ganancia = ganancia
            mejor_col = i
    return mejor_col, mejor_ganancia


def categoria_mayoritaria(datos, idx_final):
    if not datos:
        return "SinDatos"
    categorias = [fila[idx_final] for fila in datos]
    conteo = Counter(categorias)
    return conteo.most_common(1)[0][0]


def construir_arbol(datos, encabezado, indices_vars, idx_final):
    categorias_en_nodo = set(f[idx_final] for f in datos)

    if len(categorias_en_nodo) == 1:
        return list(categorias_en_nodo)[0]

    if not indices_vars:
        return categoria_mayoritaria(datos, idx_final)

    mejor_idx, mejor_ganancia = split(datos, encabezado, indices_vars, idx_final)
    if mejor_idx is None or mejor_ganancia <= 0:
        return categoria_mayoritaria(datos, idx_final)

    nombre_var = encabezado[mejor_idx]
    nodo = {nombre_var: {}}
    nuevos_indices = [i for i in indices_vars if i != mejor_idx]
    for valor in set(f[mejor_idx] for f in datos):
        subconjunto = [fila for fila in datos if fila[mejor_idx] == valor]
        if not subconjunto:
            sub_arbol = categoria_mayoritaria(datos, idx_final)
        else:
            sub_arbol = construir_arbol(subconjunto, encabezado, nuevos_indices, idx_final)
        nodo[nombre_var][valor] = sub_arbol

    return nodo


def reglas_dec(arbol, regla_actual="Si"):
    if not isinstance(arbol, dict):
        regla_limpia = regla_actual.strip().rstrip("y").strip()
        print(f"{regla_limpia} → Categoría = {arbol}")
        return

    var = list(arbol.keys())[0]
    for valor, subarbol in arbol[var].items():
        if regla_actual.strip() == "Si":
            nueva = f"{regla_actual} {var} = '{valor}'"
        else:
            nueva = f"{regla_actual} y {var} = '{valor}'"
        reglas_dec(subarbol, nueva)


def cargar_csv(ruta):
    datos = []
    header = []
    try:
        with open(ruta, 'r', encoding='utf-8-sig') as f:
            lector = csv.reader(f)
            header = next(lector)
            num_columnas = len(header)
            for fila in lector:
                if not fila or not any(fila):
                    continue
                if len(fila) != num_columnas:
                    continue
                if not fila[0].strip().isdigit():
                    continue
                datos.append(fila)

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo en la ruta: '{ruta}'")
        return None, None
    except Exception as e:
        print(f"Ocurrió un error leyendo el CSV: {e}")
        return None, None

    return header, datos


def dibujar_arbol(arbol, nombre_salida="arbol_gráfico"):
    dot = graphviz.Digraph(comment='Árbol de Decisión')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightgrey')
    contador = [0]

    def agregar_nodos(subarbol, padre=None, etiqueta=''):
        if not isinstance(subarbol, dict):
            nodo_id = f"leaf{contador[0]}"
            dot.node(nodo_id, subarbol, fillcolor='lightblue')
            if padre:
                dot.edge(padre, nodo_id, label=etiqueta)
            contador[0] += 1
            return
        var = list(subarbol.keys())[0]
        nodo_id = f"node{contador[0]}"
        dot.node(nodo_id, var)
        if padre:
            dot.edge(padre, nodo_id, label=etiqueta)
        contador[0] += 1
        for val, sub in subarbol[var].items():
            agregar_nodos(sub, nodo_id, str(val))

    try:
        agregar_nodos(arbol)
        dot.render(filename=nombre_salida, cleanup=True, format='pdf')
        dot.view(filename=nombre_salida, cleanup=True)
    except graphviz.backend.execute.ExecutableNotFound:
        exit()
    except Exception as e:
        exit()


ruta_csv = input('Ingrese el nombre del archivo .CSV:\n')
encabezado, datos = cargar_csv(ruta_csv)

if encabezado and datos:
    print(f"Columnas: {encabezado}")
    try:
        nombre_categoria_final = input("Ingrese la columna objetivo de decisión: ")
        nombre_var_inicio = input('Ingrese la columna desde donde se va a tomar en cuenta: ')

        idx_final_int = encabezado.index(nombre_categoria_final)
        idx_inicio_int = encabezado.index(nombre_var_inicio)

        indices_vars = list(range(idx_inicio_int, idx_final_int))

        print(f"Variables a analizar: {[encabezado[i] for i in indices_vars]}")

    except ValueError as e:
        print(f"Columna no encontrada")
        exit()

    arbol = construir_arbol(datos, encabezado, indices_vars, idx_final_int)

    print("\nREGLAS DE DECISIÓN\n")
    reglas_dec(arbol)
    dibujar_arbol(arbol)

else:
    print("No se pudieron cargar los datos del archivo .CSV");