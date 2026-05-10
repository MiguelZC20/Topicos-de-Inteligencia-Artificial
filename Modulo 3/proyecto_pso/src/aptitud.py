import numpy as np

"""
    FuncionAptitud:
    Clase encargada de:
        - evaluar las partículas
        - calcular fitness
        - medir cobertura de los sensores
        - analizar variabilidad ambiental
        - medir diversidad de cultivos
        - aplicar "penalizaciones"
"""
class FuncionAptitud:
    # Constructor de la clase
    def __init__(self, datos):

        self.datos = datos

        self.coordenadas = datos[
            ["Latitud", "Longitud"]
        ].values

        self.radio_cobertura = 0.015    # define el "alcance" del sensor

    """ 
        evaluar:
        Calcula el valor fitness total de cada particula (solución)
        Combina distintos criterios importantes para un sistema agricola real: 
            - cobertura: porcentaje del terreno agrícola monitoreado
            - variabilidad: condiciones del suelo
                - humedad: capturar diferentes condiciones de humedad (depende el cultivo)
                - salinidad: colocar sensores en zonas salinas distintas
                - elevacion: altura del terreno (influye en la humedad)
                - temperatura: provoca evaporacion
            - diversidad: cuantos cultivos distintos son cubiertos
            - penalizacion: sensores muy 
        Devuelve un valor númerico del fitness de la solución.
    """
    def evaluar(
        self,
        posicion_particula,
        numero_sensores
    ):

        # Cambia la forma en que se ve el vector de coordenadas
        sensores = posicion_particula.reshape(
            numero_sensores,
            2
        )

        # cobertura:
        # Mide que tanto porcentaje del terreno es cubierto por los sensores
        cobertura = (
            self.calcular_cobertura_real(
                sensores
            )
        )

        # humedad:
        # representar distintas condiciones de humedad en el terreno
        humedad = (
            self.calcular_variabilidad(
                sensores,
                "Humedad"
            )
        )

        # Variabilidad en la salinidad
        salinidad = (
            self.calcular_variabilidad(
                sensores,
                "Salinidad"
            )
        )

        # Variabilidad en la elevacion del terreno
        elevacion = (
            self.calcular_variabilidad(
                sensores,
                "Elevacion"
            )
        )

        # Variabilidad en la temperatura
        temperatura = (
            self.calcular_variabilidad(
                sensores,
                "Temperatura"
            )
        )

        # Sensor cubra los diferentes tipos de cultivos
        diversidad = (
            self.calcular_diversidad(
                sensores
            )
        )

        # Castigar sensores muy cercanos
        penalizacion = (
            self.calcular_penalizacion(
                sensores
            )
        )

        # Evitar sensores en los límites
        penalizacion_bordes = (
            self.penalizar_bordes(
                sensores
            )
        )

        """
            Función fitness

            Combina todos los criterios utilizando pesos experimentales.
        """
        fitness = (
            0.30 * cobertura
            + 0.15 * humedad
            + 0.10 * salinidad
            + 0.10 * elevacion
            + 0.10 * temperatura
            + 0.15 * diversidad
            - 0.05 * penalizacion
            - 0.05 * penalizacion_bordes
        )

        return fitness

    """
        Porcentaje de puntos (cultivos) cubiertos por los sensores.
        Un punto se considera cubierto si esta dentro del radio de al menos un sensor.
    """
    def calcular_cobertura_real(
        self,
        sensores
    ):
        # Guardar los puntos cubiertos
        puntos_cubiertos = set()

        for sensor in sensores:

            # Calcula la distancia entre sensor y los puntos agricolas (cultivos)
            distancias = np.linalg.norm(
                self.coordenadas - sensor,
                axis=1
            )

            # Busca y agrega los puntos cubiertos por el sensor
            indices = np.where(
                distancias <
                self.radio_cobertura
            )[0]

            puntos_cubiertos.update(
                indices
            )

        # Porcentaje de cobertura
        cobertura = (
            len(puntos_cubiertos)
            / len(self.coordenadas)
        )

        return cobertura

    """
        Variables de condiciones del suelo para la distribucion de los sensores 
        (humedad, salinidad, elevacion, temperatura)

        Objetivo: representar condiciones ambientales 
    """
    def calcular_variabilidad(
        self,
        sensores,
        variable
    ):
        valores = []

        for sensor in sensores:
            
            # Calcular distancias
            distancias = np.linalg.norm(
                self.coordenadas - sensor,
                axis=1
            )
            # Obtiene el punto (cultivo) más cercano
            indice = np.argmin(
                distancias
            )
            # Obtiene el valor de la variable
            valor = self.datos.iloc[
                indice
            ][variable]

            valores.append(valor)
        
        # Desviación estandar: cuanto mas grande sea, mayor diversidad ambiental
        return np.std(valores)


    """
        Calcula cuantos diferentes tipos de cultivos son cubiertos por el sensor
    """
    def calcular_diversidad(
        self,
        sensores
    ):
        cultivos = []

        for sensor in sensores:
            # Distancias hacia los puntos (cultivos)
            distancias = np.linalg.norm(
                self.coordenadas - sensor,
                axis=1
            )
            # Punto más cercano
            indice = np.argmin(
                distancias
            )
            # Obtiene tipo de cultivo
            cultivo = self.datos.iloc[
                indice
            ]["Cultivo"]

            cultivos.append(cultivo)
        
        # Se normaliza considerando los 3 tipos de cultivos del problema
        diversidad = len(set(cultivos))
        return diversidad / 3


    """
        Penalizar por sensores muy cercanos unos con otros.
        Evitar agrupamientos excesivos.
    """
    def calcular_penalizacion(
        self,
        sensores
    ):
        penalizacion = 0
        distancia_minima = 0.008

        # Comparación entre sensores
        for i in range(len(sensores)):

            for j in range(i + 1, len(sensores)):

                # Distancia entre sensores
                distancia = np.linalg.norm(
                    sensores[i] - sensores[j]
                )

                # Penaliza si están muy cerca
                if distancia < distancia_minima:

                    penalizacion += 1

        return penalizacion

    """
        Penalizar zonas prohibidas cercanas a los bordes del terreno.
    """
    def penalizar_bordes(
        self,
        sensores
    ):
        penalizacion = 0
        margen = 0.003

        # Límites geográficos
        lat_min = np.min(
            self.coordenadas[:, 0]
        )

        lat_max = np.max(
            self.coordenadas[:, 0]
        )

        lon_min = np.min(
            self.coordenadas[:, 1]
        )

        lon_max = np.max(
            self.coordenadas[:, 1]
        )

        # Analiza cada sensor
        for sensor in sensores:
            lat = sensor[0]
            lon = sensor[1]

            if (
                lat < lat_min + margen
                or lat > lat_max - margen
                or lon < lon_min + margen
                or lon > lon_max - margen
            ):
                penalizacion += 1

        return penalizacion