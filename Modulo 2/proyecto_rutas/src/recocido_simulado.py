# recocido_simulado.py

import copy
import math
import random
from dataclasses import dataclass   # para hacer el código más corto.
from typing import Any
import pandas as pd
from funcion_objetivo import calcular_distancia_total, calcular_costo_combustible_total
from vecindario import generar_vecino


"""
Importaciones:
    - copy: para copiar la estructura de las soluciones vecinas generadas.
    - math: funciones matemáticas, específicamente para el calculo de la probabilidad de aceptar soluciones peores.
    - random: generar los valores aleatorios, por ejemplo para decidir si una solución peor se acepta.
    - dataclass: crear clases para almacenar datos (por ejemplo, no hace falta escribir el constructor).
    - Any: para guardar valores de cualquier tipo.
    - pandas: para manejar dataframes (la matriz de distancias).
    - calcular_distancia_total, calcular_costo_combustible_total: funciones del modulo funcion_objetivo.
    - generar_vecino: función del modulo vecindario. 
"""

"""
ResultadoRecocido:
Clase de datos para guardar los resultados del algoritmo.
    - mejor_solucion: las rutas con menor distancia.
    - mejor_distancia: distancia total de la mejor solución.
    - mejor_costo_combustible: costo de combustible de la mejor solución.
    - solucion_final: guarda la última solución con la que termino el algoritmo (aunque no sea la mejor).
    - distancia_final: distancia de la solución final.
    - costo_combustible_final: costo de combustible de la solución final.
    - historial: guarda la evolución del algoritmo con cada iteración (temperatura, costo actual, mejor costo).
    - criterio_parada: indica por qué terminó el algoritmo.
    - temperatura_final: temperatura cuando el algoritmo se detuvo.
"""
@dataclass
class ResultadoRecocido:
    mejor_solucion: list[list[int]]
    mejor_distancia: float
    mejor_costo_combustible: float
    solucion_final: list[list[int]]
    distancia_final: float
    costo_combustible_final: float
    historial: list[dict[str, Any]]
    criterio_parada: str
    temperatura_final: float


"""
calcular_temperatura_inicial:
Calcula y devuelve una temperatura inicial a partir del costo de la solución inicial.
    - solucion_inicial: solución con la que arranca el algoritmo.
    - centros: lista de los centros de distribución.
    - matriz_distancias: archivo con la matriz usada para calcular la distancia.
    - factor: es un factor multiplicador para calcular la temperatura incial en propoción
        con el costo inicial.
    - temperataura_minima: evitar que la temperatura sea cero.
"""
def calcular_temperatura_inicial(
    solucion_inicial: list[list[int]],
    centros: list[int],
    matriz_distancias: pd.DataFrame,
    factor: float = 0.5,
    temperatura_minima: float = 1e-6,
) -> float:
    distancia_inicial = calcular_distancia_total(solucion_inicial, centros, matriz_distancias)
    return float(max(distancia_inicial * factor, temperatura_minima))


"""
aceptar_vecino:
Decide si una solucion vecina es aceptada o no.
    - costo_actual: costo de la mejor solución actual.
    - costo_vecino: costo de la solución candidata.
    - temperatura: la temperatura en la que se encuentra el algoritmo.
    - delta: calculo de la diferencia entre la solución actual y la candidata.
    - (-delta / temperatura): calcula la probabilidad de aceptación.
        -random.random(): genera un número entre 0 y 1.
        -si el numero generado es menor que la probabilidad, se acepta la solución.
"""
def aceptar_vecino(costo_actual: float, costo_vecino: float, temperatura: float) -> bool:
    delta = costo_vecino - costo_actual
    if delta <= 0:
        return True
    if temperatura <= 0:
        return False
    return random.random() < math.exp(-delta / temperatura)


"""
recocido_simulado:
Ejecuta el algoritmo de recocido simulado.
    - solucion_inicial: solución de la que parte el algoritmo.
    - centros: lista de los centros de distribución.
    - matriz_distancias: archivo con la matriz usada para evaluar las rutas.
    - temperatura_inicial: temperatura con la que inicia el algoritmo (se puede indicar o se calcula automáticamente).
    - factor_enfriamiento: parámetro que reduce la temperatura en cada iteración.
    - temperatura_minima: temperatura en la que el algoritmo se detiene.
    - iteraciones_por_temperatura: número de soluciones generadas antes de pasar a la siguiente temperatura.
    - max_iteraciones_totales: límite total de iteraciones.
    - limite_sin_mejora: si el algoritmo no mejora durante n iteraciones, se detiene.
    - semilla: permite reproducir la aleatoriedad.
    - mostrar_temperatura: imprime la temperatura por consola.
"""
def recocido_simulado(
    solucion_inicial: list[list[int]],
    centros: list[int],
    matriz_distancias: pd.DataFrame,
    temperatura_inicial: float | None = None,
    factor_enfriamiento: float = 0.98,
    temperatura_minima: float = 1e-3,   # 0.001
    iteraciones_por_temperatura: int = 100,
    max_iteraciones_totales: int = 10000,
    limite_sin_mejora: int = 1000,
    semilla: int | None = None,
    mostrar_temperatura: bool = True,
) -> ResultadoRecocido:
    if semilla is not None:
        random.seed(semilla)    # poder reproducir los mismos resultados

    solucion_actual = copy.deepcopy(solucion_inicial) # copia de la solución que se va modificando
    mejor_solucion = copy.deepcopy(solucion_inicial)  # copia de la mejor solución hasta el momento

    # distancia de la solución inicial se guarda como la mejor actual
    distancia_actual = calcular_distancia_total(solucion_actual, centros, matriz_distancias)
    mejor_distancia = distancia_actual

    # si no se proporciona la temperatura inicial, se calcula con la función
    temperatura = (
        calcular_temperatura_inicial(solucion_actual, centros, matriz_distancias)
        if temperatura_inicial is None
        else float(temperatura_inicial)
    )

    # guarda el costo (distancia) actual en cada iteración
    costo_actual = distancia_actual 

    # costo de combustible de la mejor solución encontrada
    mejor_costo_combustible = calcular_costo_combustible_total(mejor_distancia) 

    # guardar la evolución del algoritmo
    historial: list[dict[str, Any]] = []
    iteracion_total = 0                     # número de vecinos evaluados
    iteraciones_sin_mejora = 0              # número de ieraciones sin mejorar la solución
    criterio_parada = "No definido"


    # bucle principal: se detiene mediante condiciones
    while True:
        if temperatura <= temperatura_minima:
            criterio_parada = "Temperatura mínima alcanzada"
            break
        if iteracion_total >= max_iteraciones_totales:
            criterio_parada = "Máximo de iteraciones totales alcanzado"
            break
        if iteraciones_sin_mejora >= limite_sin_mejora:
            criterio_parada = "Límite de iteraciones sin mejora alcanzado"
            break

        # muestra por consola el estado actual del algoritmo para observar el enfríamiento y la mejora
        if mostrar_temperatura:
            print(
                f"Temperatura actual: {temperatura:.6f} | "
                f"Mejor distancia: {mejor_distancia:.4f} | "
                f"Distancia actual: {costo_actual:.4f}"
            )

        # cantidad de vecinos generados antes de enfríar el algoritmo
        for _ in range(iteraciones_por_temperatura):
            if iteracion_total >= max_iteraciones_totales:
                criterio_parada = "Máximo de iteraciones totales alcanzado"
                break
            if iteraciones_sin_mejora >= limite_sin_mejora:
                criterio_parada = "Límite de iteraciones sin mejora alcanzado"
                break

            solucion_vecina = generar_vecino(solucion_actual)
            distancia_vecina = calcular_distancia_total(solucion_vecina, centros, matriz_distancias)

            # decidir si la solución vecina se acepta
            if aceptar_vecino(costo_actual, distancia_vecina, temperatura):
                solucion_actual = solucion_vecina
                costo_actual = distancia_vecina

                if costo_actual <= mejor_distancia:
                    mejor_solucion = copy.deepcopy(solucion_actual)
                    mejor_distancia = costo_actual
                    mejor_costo_combustible = calcular_costo_combustible_total(mejor_distancia)
                    iteraciones_sin_mejora = 0
                else:
                    iteraciones_sin_mejora += 1
            else:
                iteraciones_sin_mejora += 1

            iteracion_total += 1

            # guardar el estado de la iteración
            historial.append(
                {
                    "iteracion": iteracion_total,
                    "temperatura": temperatura,
                    "distancia_actual": costo_actual,
                    "mejor_distancia": mejor_distancia,
                }
            )

        if criterio_parada != "No definido":
            break

        # reducir la temperatura
        temperatura *= factor_enfriamiento

    # guardar el resultado final de la ejecución
    # distancia y costo de combustible en la que terminó el algoritmo 
    distancia_final = costo_actual  
    costo_combustible_final = calcular_costo_combustible_total(distancia_final)

    # devuelve un objeto ResultadoRecocido con la información importante
    return ResultadoRecocido(
        mejor_solucion=mejor_solucion,
        mejor_distancia=mejor_distancia,
        mejor_costo_combustible=mejor_costo_combustible,
        solucion_final=solucion_actual,
        distancia_final=distancia_final,
        costo_combustible_final=costo_combustible_final,
        historial=historial,
        criterio_parada=criterio_parada,
        temperatura_final=temperatura,
    )
