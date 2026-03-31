# vecindario.py

import copy
import random

# Invierte un segmento de una ruta seleccionada
# Es decir, cambia el orden de visita de las tiendas en una ruta
def invertir_segmento_ruta(solucion: list[list[int]]) -> list[list[int]]:
    nueva_solucion = copy.deepcopy(solucion)

    rutas_validas = [
        indice for indice, ruta in enumerate(nueva_solucion) if len(ruta) >= 2
    ]

    if not rutas_validas:
        return nueva_solucion

    indice_ruta = random.choice(rutas_validas)
    ruta = nueva_solucion[indice_ruta]

    i, j = sorted(random.sample(range(len(ruta)), 2))
    ruta[i:j + 1] = list(reversed(ruta[i:j + 1]))

    return nueva_solucion


def generar_vecino(solucion: list[list[int]]) -> list[list[int]]:
    return invertir_segmento_ruta(solucion)