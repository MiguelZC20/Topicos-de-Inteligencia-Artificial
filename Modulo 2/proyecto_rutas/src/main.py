# main.py

from pathlib import Path    # para trabajar con rutas de archivos de forma limpia
from cargar_datos import (
    cargar_archivo_distribucion,
    cargar_matriz,
    obtener_centros_y_tiendas,
    obtener_nombre_por_id,
    obtener_zona_por_id,
    preparar_datos_problema,
)
from solucion_inicial import construir_solucion_inicial
from recocido_simulado import recocido_simulado

# carpeta raíz del proyecto
DIRECTORIO_BASE = Path(__file__).resolve().parent.parent
# archivo con la infromación de los centros de distribución y las tiendas
ARCHIVO_DISTRIBUCION = DIRECTORIO_BASE / "data" / "datos_distribucion_tiendas_con_zona.xlsx"
# archivo con la matriz de distancias
ARCHIVO_DISTANCIAS = DIRECTORIO_BASE / "data" / "matriz_distancias_geografica.xlsx"

# mostrar en pantalla de forma legible la ruta 
def mostrar_ruta(indice_ruta: int, ruta: list[int], nombres_por_id: dict[int, str], zonas_por_id: dict[int, str]) -> None:
    partes = [f"{nombres_por_id.get(nodo, str(nodo))} ({zonas_por_id.get(nodo, 'Sin zona')})" for nodo in ruta]
    print(f"Ruta {indice_ruta} = {' -> '.join(partes) if partes else '(ruta vacía)'}")

# mostrar todas las rutas de la solución
def mostrar_solucion(titulo: str, solucion: list[list[int]], nombres_por_id: dict[int, str], zonas_por_id: dict[int, str]) -> None:
    print(f"\n{titulo}")
    for indice, ruta in enumerate(solucion, start=1):
        mostrar_ruta(indice, ruta, nombres_por_id, zonas_por_id)

# ejecución del algoritmo 
def main() -> None:
    datos = cargar_archivo_distribucion(ARCHIVO_DISTRIBUCION)
    matriz_distancias = cargar_matriz(ARCHIVO_DISTANCIAS)

    datos = preparar_datos_problema(datos)
    centros, tiendas = obtener_centros_y_tiendas(datos)
    nombres_por_id = obtener_nombre_por_id(datos)
    zonas_por_id = obtener_zona_por_id(datos)

    solucion_inicial = construir_solucion_inicial(centros, tiendas, matriz_distancias)

    print("=== SOLUCIÓN INICIAL ===")
    mostrar_solucion("Rutas iniciales:", solucion_inicial, nombres_por_id, zonas_por_id)

    distancia_inicial = sum(
        0 for _ in [0]
    )

    resultado = recocido_simulado(
        solucion_inicial=solucion_inicial,
        centros=centros,
        matriz_distancias=matriz_distancias,
        temperatura_inicial=None,
        factor_enfriamiento=0.98,
        temperatura_minima=1e-3,    # 0.001
        iteraciones_por_temperatura=100,
        max_iteraciones_totales=10000,
        limite_sin_mejora=1000,
        semilla=None,
        mostrar_temperatura=True,
    )

    distancia_inicial = resultado.historial[0]["distancia_actual"] if resultado.historial else resultado.distancia_final
    costo_combustible_inicial = distancia_inicial * 0.15

    print("\n--- SOLUCIÓN INICIAL ---")
    print(f"Distancia total: {distancia_inicial:.4f}")
    print(f"Costo de combustible: {costo_combustible_inicial:.4f}")

    print("\n--- CRITERIO DE PARADA ---")
    print(resultado.criterio_parada)

    print("\n--- RESULTADO DEL RECOCIDO SIMULADO --")
    print(f"Mejor distancia encontrada: {resultado.mejor_distancia:.4f}")
    print(f"Mejor costo de combustible: {resultado.mejor_costo_combustible:.4f}")

    mostrar_solucion("Rutas de la mejor solución:", resultado.mejor_solucion, nombres_por_id, zonas_por_id)


if __name__ == "__main__":
    main()
