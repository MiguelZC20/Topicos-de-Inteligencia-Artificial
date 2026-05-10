import numpy as np


""""
    Clase que representa a una particula en el PSO.
    Cada particula es una posible solución.
    Una particula contiene:
        - posicion 
        - velocidad
        - valor de fitness
        - mejor posicion encontrada
        - mejor valor de fitness encontrado
"""
class Particula:
    # Constructor de la clase
    def __init__(
        self,
        numero_sensores,
        limites_latitud,
        limites_longitud
    ):
        # Número de sensores definidos para la solución
        self.numero_sensores = numero_sensores

        # Límites del terreno
        self.limites_latitud = limites_latitud
        self.limites_longitud = limites_longitud

        self.dimension = numero_sensores * 2

        # Posición actual (inicia de forma aleatoria)
        self.posicion = (
            self.inicializar_posicion()
        )

        # Velocidad inicial = 0
        self.velocidad = np.zeros(
            self.dimension
        )

        # Fitness actual (guardar el valor de la solución actual)
        self.aptitud = float("-inf")

        # Mejor posición encontrada 
        self.mejor_posicion = (
            self.posicion.copy()
        )

        # Mejor valor fitness encontrado
        self.mejor_aptitud = float("-inf")


    """
        Genera una posición aleateoria para la particula.
        Los sensores reciben una latitud y longitud aleatoria.
        Devuelve un vector con las coordenadas de los sensores. 
    """
    def inicializar_posicion(self):

        posicion = []

        for _ in range(self.numero_sensores):

            # Latitud aleatoria dentro de los límites
            latitud = np.random.uniform(
                self.limites_latitud[0],
                self.limites_latitud[1]
            )
            # Longitud aleatoria dentro de los límites
            longitud = np.random.uniform(
                self.limites_longitud[0],
                self.limites_longitud[1]
            )

            # Vector de posicion
            posicion.extend([
                latitud,
                longitud
            ])

        return np.array(posicion)


    """
        Se actualiza la posición de la particula sumando:
            posicion actual + velocidad
        Se verifican los límites del terreno para evitar posiciones invalidas.
    """
    def actualizar_posicion(self):

        self.posicion = (
            self.posicion + self.velocidad
        )

        self.aplicar_limites()


    """
        Restringe las coordenadas de la particula a los límites del terreno.
        Si alguna particula se sale de los límites, entonces se ajusta automaticamente.
    """
    def aplicar_limites(self):

        for i in range(0, self.dimension, 2):

            # Latitud
            self.posicion[i] = np.clip(
                self.posicion[i],
                self.limites_latitud[0],
                self.limites_latitud[1]
            )

            # Longitud
            self.posicion[i + 1] = np.clip(
                self.posicion[i + 1],
                self.limites_longitud[0],
                self.limites_longitud[1]
            )