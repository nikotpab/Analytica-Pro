import csv
import math
from collections import Counter
import sys
import json


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
        reglas_lista.append(f"{regla_limpia} -> Categoría = {arbol}")
        return reglas_lista

    var = list(arbol.keys())[0]
    for valor, subarbol in arbol[var].items():
        nueva = f"{regla_actual} {var} = '{valor}'" if regla_actual.strip() == "Si" else f"{regla_actual} y {var} = '{valor}'"
        get_reglas_dec_text(subarbol, nueva, reglas_lista)
    return reglas_lista


def cargar_csv(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8-sig') as f:
            header_line = f.readline()
            f.seek(0)
            if header_line.count(';') > header_line.count(','):
                delimiter = ';'
            else:
                delimiter = ','

            lector = csv.reader(f, delimiter=delimiter)
            header = next(lector)
            datos = [fila for fila in lector if fila and any(fila) and len(fila) == len(header)]
        return header, datos
    except (FileNotFoundError, Exception) as e:
        return None, None