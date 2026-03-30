# funcion_objetivo.py

import pandas as pd

# Obtiene la distancia entre dos nodos usando su posición en la matriz.
def obtener_distancia(matriz_distancias: pd.DataFrame, nodo_origen: int, nodo_destino: int) -> float:
    return float(matriz_distancias.iloc[nodo_origen - 1, nodo_destino - 1])


"""
Calcula la distancia total de una ruta.
La ruta inicia en el centro de distribución, visita las tiendas y regresa al mismo centro.
"""
def calcular_distancia_ruta(
    centro_id: int,
    ruta: list[int],
    matriz_distancias: pd.DataFrame
) -> float:
    if not ruta:
        return 0.0

    distancia_total = 0.0
    nodo_anterior = centro_id

    for tienda in ruta:
        distancia_total += obtener_distancia(matriz_distancias, nodo_anterior, tienda)
        nodo_anterior = tienda

    distancia_total += obtener_distancia(matriz_distancias, nodo_anterior, centro_id)
    return distancia_total


# Suma la distancia de todas las rutas de la solución.
def calcular_distancia_total(
    solucion: list[list[int]],
    centros: list[int],
    matriz_distancias: pd.DataFrame
) -> float:
    
    distancia_total = 0.0

    for indice_centro, ruta in enumerate(solucion):
        centro_id = centros[indice_centro]
        distancia_total += calcular_distancia_ruta(centro_id, ruta, matriz_distancias)

    return distancia_total


"""
Convierte la distancia total en costo de combustible usando un factor fijo.
En este proyecto se usa el factor 0.15 porque la matriz de costos de combustible está
proporcionalmente relacionada con la distancia.
"""
def calcular_costo_combustible_total(distancia_total: float, factor_combustible: float = 0.15) -> float:
    return distancia_total * factor_combustible
