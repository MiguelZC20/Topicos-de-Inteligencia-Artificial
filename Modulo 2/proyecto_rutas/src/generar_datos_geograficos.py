# generar_datos_geograficos.py
# modulo auxiliar
from pathlib import Path
import math
import numpy as np
import pandas as pd


DIRECTORIO_BASE = Path(__file__).resolve().parent.parent

# Archivo original con la información base del problema
ARCHIVO_ORIGINAL = DIRECTORIO_BASE / "data" / "datos_distribucion_tiendas.xlsx"

# Archivos que se generarán a partir de las coordenadas reales
ARCHIVO_SALIDA_DISTANCIAS = DIRECTORIO_BASE / "data" / "matriz_distancias_geografica.xlsx"
ARCHIVO_SALIDA_COSTOS = DIRECTORIO_BASE / "data" / "matriz_costos_combustible_geografica.xlsx"
    
# Calcula la distancia geodésica entre dos puntos en kilómetros
def distancia_haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radio_tierra_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radio_tierra_km * math.asin(math.sqrt(a))

# Construye una matriz cuadrada de distancias a partir de latitud y longitud
def construir_matriz_distancias(coordenadas: np.ndarray) -> pd.DataFrame:
    cantidad_nodos = len(coordenadas)
    matriz = np.zeros((cantidad_nodos, cantidad_nodos), dtype=float)

    for i in range(cantidad_nodos):
        lat1, lon1 = coordenadas[i]
        for j in range(i + 1, cantidad_nodos):
            lat2, lon2 = coordenadas[j]
            distancia = distancia_haversine_km(lat1, lon1, lat2, lon2)
            matriz[i, j] = distancia
            matriz[j, i] = distancia

    nombres_columnas = [f"Nodo_{i}" for i in range(1, cantidad_nodos + 1)]
    return pd.DataFrame(matriz, columns=nombres_columnas)



# Lee el archivo original y genera las matrices geográficas de distancias y costos
def main() -> None:
    if not ARCHIVO_ORIGINAL.exists():
        raise FileNotFoundError(f"No se encontró el archivo original: {ARCHIVO_ORIGINAL}")

    datos = pd.read_excel(ARCHIVO_ORIGINAL)

    columnas_requeridas = {"Tipo", "Nombre", "Latitud_WGS84", "Longitud_WGS84"}
    faltantes = columnas_requeridas - set(datos.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas en el archivo original: {faltantes}")

    # 1) Construir la matriz de distancias con base en coordenadas reales
    coordenadas = datos[["Latitud_WGS84", "Longitud_WGS84"]].to_numpy()
    matriz_distancias = construir_matriz_distancias(coordenadas)

    # 2) Construir la matriz de costos a partir de la distancia
    factor_combustible = 0.15
    matriz_costos = matriz_distancias * factor_combustible

    # 3) Guardar archivos procesados
    matriz_distancias.to_excel(ARCHIVO_SALIDA_DISTANCIAS, index=False)
    matriz_costos.to_excel(ARCHIVO_SALIDA_COSTOS, index=False)

    print("Archivos generados correctamente:")
    print(" -", ARCHIVO_SALIDA_DISTANCIAS)
    print(" -", ARCHIVO_SALIDA_COSTOS)

if __name__ == "__main__":
    main()
