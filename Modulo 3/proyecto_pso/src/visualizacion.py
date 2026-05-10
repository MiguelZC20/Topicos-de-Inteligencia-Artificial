import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


class VisualizadorPSO:

    def __init__(self, datos):

        self.datos = datos

    def graficar_terreno_y_sensores(
        self,
        mejor_posicion,
        numero_sensores
    ):

        sensores = mejor_posicion.reshape(
            numero_sensores,
            2
        )

        plt.figure(figsize=(10, 8))

        sns.scatterplot(
            data=self.datos,
            x="Longitud",
            y="Latitud",
            hue="Cultivo",
            palette="Set1",
            s=80
        )

        plt.scatter(
            sensores[:, 1],
            sensores[:, 0],
            color="black",
            marker="X",
            s=250,
            label="Sensores"
        )

        plt.title(
            "Distribución Óptima de Sensores"
        )

        plt.xlabel("Longitud")
        plt.ylabel("Latitud")

        plt.legend()

        plt.grid(True)

        plt.show()

    def graficar_convergencia(
        self,
        historial_aptitud
    ):

        plt.figure(figsize=(10, 6))

        plt.plot(
            historial_aptitud,
            linewidth=2
        )

        plt.title(
            "Convergencia del PSO"
        )

        plt.xlabel("Iteraciones")

        plt.ylabel(
            "Mejor Aptitud"
        )

        plt.grid(True)

        plt.show()