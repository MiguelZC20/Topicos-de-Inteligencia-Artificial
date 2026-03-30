# solucion_inicial.py

import random
import pandas as pd

# Obtiene la distancia entre dos nodos usando su posición en la matriz
def obtener_distancia(matriz_distancias: pd.DataFrame, nodo_origen: int, nodo_destino: int) -> float:    
    return float(matriz_distancias.iloc[nodo_origen - 1, nodo_destino - 1])


"""
Construye una solución inicial aleatoria:
    1. Mezclar aleatoriamente las tiendas.
    2. Repartirlas entre los centros de distribución.
    3. Intercambiar el orden dentro de cada ruta.
"""
def construir_solucion_inicial(
    centros: list[int],
    tiendas: list[int],
    matriz_distancias: pd.DataFrame
) -> list[list[int]]:
    # Copia de la lista de tiendas para no modificar la original
    tiendas_aleatorias = tiendas.copy()

    # Se mezclan las tiendas en orden aleatorio
    random.shuffle(tiendas_aleatorias)

    # Se crea una ruta vacía por cada centro de distribución
    rutas = [[] for _ in centros]

    # Reparto de tiendas entre las rutas
    for indice, tienda in enumerate(tiendas_aleatorias):
        indice_ruta = indice % len(centros)
        rutas[indice_ruta].append(tienda)

    # Se mezcla el orden interno de cada ruta
    for ruta in rutas:
        random.shuffle(ruta)

    return rutas