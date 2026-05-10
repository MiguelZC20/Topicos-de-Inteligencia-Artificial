import pandas as pd
from sklearn.preprocessing import MinMaxScaler


class PreprocesadorDatos:

    def __init__(self, ruta_archivo):

        self.ruta_archivo = ruta_archivo
        self.datos = None

    def cargar_datos(self):

        self.datos = pd.read_excel(self.ruta_archivo)

        self.datos.columns = (
            self.datos.columns.str.strip()
        )

        return self.datos

    def codificar_cultivos(self):

        mapa_cultivos = {
            "Maiz": 0,
            "Chile": 1,
            "Tomate": 2
        }

        self.datos["Cultivo"] = (
            self.datos["Cultivo"]
            .map(mapa_cultivos)
        )

    def normalizar_variables(self):

        columnas = [
            "Humedad",
            "Elevacion",
            "Salinidad",
            "Temperatura"
        ]

        escalador = MinMaxScaler()

        self.datos[columnas] = (
            escalador.fit_transform(
                self.datos[columnas]
            )
        )

    def ejecutar_preprocesamiento(self):

        self.cargar_datos()

        self.codificar_cultivos()

        self.normalizar_variables()

        return self.datos