# solucion_inicial.py

import random
import pandas as pd

"""
Construye una solución inicial aleatoria:
    - Mezclar aleatoriamente las tiendas.
    - Asignarlas entre los centros de distribución.
    - Intercambiar el orden dentro de cada ruta.
"""
def construir_solucion_inicial(
    centros: list[int],
    tiendas: list[int],
    matriz_distancias: pd.DataFrame
) -> list[list[int]]:
    tiendas_aleatorias = tiendas.copy()

    # se mezclan las tiendas en orden aleatorio
    random.shuffle(tiendas_aleatorias)

    # se crea una ruta vacía por cada centro de distribución
    rutas = [[] for _ in centros]

    # asignación de tiendas entre las rutas
    for indice, tienda in enumerate(tiendas_aleatorias):
        indice_ruta = indice % len(centros)
        rutas[indice_ruta].append(tienda)

    # mezclar el orden interno de cada ruta
    for ruta in rutas:
        random.shuffle(ruta)

    return rutas