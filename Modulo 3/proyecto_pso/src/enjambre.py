import numpy as np
from particula import Particula
from aptitud import FuncionAptitud


"""
    Clase principal que implementa al PSO.
    Un enjambre esta compuesto por multiples particulas (solución).
    El enjambre se encarga de:
        - Crear las particulas
        - Evaluar las particulas (soluciones)
        - Actualizar velocidades
        - Actualizar posiciones
        - Guardar la mejor solucion global
        - Repetir el proceso
"""
class EnjambrePSO:
    # Constructor de la clase 
    def __init__(
        self,
        datos,
        numero_particulas,
        numero_sensores,
        iteraciones
    ):
        # Datos del terreno 
        self.datos = datos

        # Número de particulas del enjambre definidas
        self.numero_particulas = (
            numero_particulas
        )

        # Número de sensores definido que tendra cada solución
        self.numero_sensores = (
            numero_sensores
        )

        # Número total de iteraciones 
        self.iteraciones = iteraciones

        """
            Parámetros del PSO:
                w -> componente de inercia: cuanto mantiene la particula su velocidad anterior.
                c1 -> componente cognitivo: influencia hacia la mejor solución individual.
                c2 -> componente social: influencia hacia la mejor solución global.
        """
        self.w = 0.8
        self.c1 = 2
        self.c2 = 2

        # Valores minimo y maximo de latitud
        self.limites_latitud = (
            datos["Latitud"].min(),
            datos["Latitud"].max()
        )

        # valores minimo y maximo de longitud
        self.limites_longitud = (
            datos["Longitud"].min(),
            datos["Longitud"].max()
        )

        # Evaluar la calidad de cada solución
        self.funcion_aptitud = (
            FuncionAptitud(datos)
        )

        # Creación del enjambre
        self.particulas = (
            self.inicializar_particulas()
        )

        # Mejor posición encontrada por el enjambre
        self.mejor_posicion_global = None

        # Mejor valor fitness del enjambre
        self.mejor_aptitud_global = (
            float("-inf")
        )

        # Guardar la evolucion del valor fitness
        self.historial_aptitud = []


    """
        Crea todas las particulas del enjambre.
        Cada particula recibe:
            - número de sensores
            - límites de latitud
            - límites de longitud
        Regresa una lista con todas las particulas.
    """
    def inicializar_particulas(self):
        particulas = []

        for _ in range(
            self.numero_particulas
        ):

            particula = Particula(
                self.numero_sensores,
                self.limites_latitud,
                self.limites_longitud
            )

            particulas.append(
                particula
            )

        return particulas

    """
        Se evalua el valor fitness de todas las particulas.
        Se actualiza:
            - la mejor posición individual de cada particula (pBest)
            - la mejor posición encontra por el enjambre (gBest)
    """
    def evaluar_particulas(self):
        for particula in self.particulas:
            aptitud = (
                self.funcion_aptitud.evaluar(
                    particula.posicion,
                    self.numero_sensores
                )
            )

            # Guardar el valor fitness actual
            particula.aptitud = aptitud

            # Si la solución actual es mejor que la mejor encontrada:
            # se actualiza pBest
            if (
                aptitud >
                particula.mejor_aptitud
            ):

                particula.mejor_aptitud = (
                    aptitud
                )

                particula.mejor_posicion = (
                    particula.posicion.copy()
                )

            # Si la solucion actual supera a la mejor global del enjambre
            if (
                aptitud >
                self.mejor_aptitud_global
            ):
                # Nuevo mejor valor de fitness global
                self.mejor_aptitud_global = (
                    aptitud
                )
                # Nueva mejor posición global
                self.mejor_posicion_global = (
                    particula.posicion.copy()
                )

    """
        Actualiza la velocidad de todas las particulas usando la formula clásica del PSO.
        La velocidad depende de:
            - inercia
            - componente cognitivo
            - componente social
    """
    def actualizar_velocidades(self):
        for particula in self.particulas:

            # Valor aleatorios para exploración.
            # r1 es para cognitivo y r2 para social.
            r1 = np.random.random(
                particula.dimension
            )

            r2 = np.random.random(
                particula.dimension
            )

            # Componente cognitivo: 
            # La particula intenta ir hacia su mejor solución (pBest).
            componente_cognitivo = (
                self.c1 * r1 * (particula.mejor_posicion - particula.posicion)
            )

            # Componente social:
            # La particula es atraida hacia la mejor solución encontrada (gBest)
            componente_social = (
                self.c2 * r2 * (self.mejor_posicion_global - particula.posicion)
            )

            # La formúla de actualización
            nueva_velocidad = (
                self.w * particula.velocidad + componente_cognitivo + componente_social
            )

            particula.velocidad = (
                nueva_velocidad
            )

    """
        Actualiza la posición de todas las particulas con su velocidad actual
    """
    def actualizar_posiciones(self):
        for particula in self.particulas:
            particula.actualizar_posicion()

    """
        Flujo completo del algoritmo PSO
    """
    def ejecutar_optimizacion(self):
        for iteracion in range(
            self.iteraciones
        ):
            self.evaluar_particulas()

            self.actualizar_velocidades()

            self.actualizar_posiciones()

            self.historial_aptitud.append(
                self.mejor_aptitud_global
            )

            print(
                f"Iteración "
                f"{iteracion + 1} | "
                f"Mejor aptitud: "
                f"{self.mejor_aptitud_global:.4f}"
            )

        return (
            self.mejor_posicion_global,
            self.mejor_aptitud_global
        )