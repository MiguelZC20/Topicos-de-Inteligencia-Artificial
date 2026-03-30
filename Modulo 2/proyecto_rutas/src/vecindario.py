# vecindario.py

import copy
import random

# Obtiene los índices de las rutas que contienen al menos una tienda.
def _obtener_indices_rutas_no_vacias(solucion: list[list[int]]) -> list[int]:
    return [indice for indice, ruta in enumerate(solucion) if len(ruta) > 0]


# Mueve una tienda de una ruta a otra ruta distinta.
def mover_tienda_entre_rutas(solucion: list[list[int]]) -> list[list[int]]:
    nueva_solucion = copy.deepcopy(solucion)
    rutas_no_vacias = _obtener_indices_rutas_no_vacias(nueva_solucion)

    if not rutas_no_vacias:
        return nueva_solucion

    indice_origen = random.choice(rutas_no_vacias)
    if not nueva_solucion[indice_origen]:
        return nueva_solucion

    tienda = random.choice(nueva_solucion[indice_origen])
    nueva_solucion[indice_origen].remove(tienda)

    rutas_destino = [i for i in range(len(nueva_solucion)) if i != indice_origen]
    if not rutas_destino:
        nueva_solucion[indice_origen].append(tienda)
        return nueva_solucion

    indice_destino = random.choice(rutas_destino)
    posicion_insercion = random.randint(0, len(nueva_solucion[indice_destino]))
    nueva_solucion[indice_destino].insert(posicion_insercion, tienda)

    return nueva_solucion


# Intercambia dos tiendas entre dos rutas distintas.
def intercambiar_tiendas_entre_rutas(solucion: list[list[int]]) -> list[list[int]]:  
    nueva_solucion = copy.deepcopy(solucion)
    rutas_no_vacias = _obtener_indices_rutas_no_vacias(nueva_solucion)

    if not rutas_no_vacias:
        return nueva_solucion

    # Si solo hay una ruta con tiendas, se intenta un intercambio interno.
    if len(rutas_no_vacias) == 1:
        indice_ruta = rutas_no_vacias[0]
        if len(nueva_solucion[indice_ruta]) < 2:
            return nueva_solucion

        i, j = random.sample(range(len(nueva_solucion[indice_ruta])), 2)
        nueva_solucion[indice_ruta][i], nueva_solucion[indice_ruta][j] = (
            nueva_solucion[indice_ruta][j],
            nueva_solucion[indice_ruta][i],
        )
        return nueva_solucion

    # Si hay al menos dos rutas con tiendas, se intercambian dos nodos.
    indice_ruta_1, indice_ruta_2 = random.sample(rutas_no_vacias, 2)

    if not nueva_solucion[indice_ruta_1] or not nueva_solucion[indice_ruta_2]:
        return nueva_solucion

    tienda_1 = random.choice(nueva_solucion[indice_ruta_1])
    tienda_2 = random.choice(nueva_solucion[indice_ruta_2])

    posicion_1 = nueva_solucion[indice_ruta_1].index(tienda_1)
    posicion_2 = nueva_solucion[indice_ruta_2].index(tienda_2)

    nueva_solucion[indice_ruta_1][posicion_1] = tienda_2
    nueva_solucion[indice_ruta_2][posicion_2] = tienda_1

    return nueva_solucion


# Invierte un segmento de una ruta seleccionada.
# Es decir, cambia el orden de visita de las tiendas en una ruta.
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


"""
Genera una solución vecina eligiendo aleatoriamente uno de estos movimientos:
    - mover una tienda entre rutas.
    - intercambiar tiendas entre rutas.
    - invertir un segmento de una ruta.
"""
def generar_vecino(solucion: list[list[int]]) -> list[list[int]]:
    tipo_movimiento = random.choice([
        "mover",
        "intercambiar",
        "invertir",
    ])

    if tipo_movimiento == "mover":
        return mover_tienda_entre_rutas(solucion)
    elif tipo_movimiento == "intercambiar":
        return intercambiar_tiendas_entre_rutas(solucion)
    else:
        return invertir_segmento_ruta(solucion)