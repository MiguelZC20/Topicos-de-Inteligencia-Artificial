import numpy as np


class Terreno:

    def __init__(self, datos):

        self.datos = datos
        self.matriz_terreno = None

    def construir_matriz(self):

        self.matriz_terreno = self.datos.to_numpy()

        return self.matriz_terreno

    def obtener_coordenadas(self):

        coordenadas = self.datos[
            ["Latitud", "Longitud"]
        ].values

        return coordenadas

    def obtener_variables_agricolas(self):

        variables = self.datos[
            [
                "Humedad",
                "Cultivo",
                "Elevacion",
                "Salinidad",
                "Temperatura"
            ]
        ].values

        return variables

    def obtener_dimensiones(self):

        return self.matriz_terreno.shape