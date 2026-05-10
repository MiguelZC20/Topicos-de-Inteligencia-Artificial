from preprocesamiento import PreprocesadorDatos
from terreno import Terreno
from particula import Particula
from aptitud import FuncionAptitud
from enjambre import EnjambrePSO
from visualizacion import VisualizadorPSO

def main():
    ruta_archivo = "../datos/datos_agricolas.xlsx"

    print("Cargando datos agrícolas...\n")

    preprocesador = PreprocesadorDatos(
        ruta_archivo
    )

    datos_procesados = (
        preprocesador
        .ejecutar_preprocesamiento()
    )

    print("Datos procesados correctamente:\n")

    print(datos_procesados.head())

    print("\nConstruyendo representación del terreno...\n")

    terreno = Terreno(datos_procesados)

    matriz_terreno = (
        terreno.construir_matriz()
    )

    coordenadas = (
        terreno.obtener_coordenadas()
    )

    dimensiones = (
        terreno.obtener_dimensiones()
    )

    print("Dimensiones del terreno:")

    print(dimensiones)


    # Algoritmo PSO
    print("\nIniciando algoritmo PSO...\n")

    enjambre = EnjambrePSO(
        datos=datos_procesados,
        numero_particulas=100,
        numero_sensores=10,
        iteraciones=50
    )

    mejor_posicion, mejor_aptitud = (
        enjambre.ejecutar_optimizacion()
    )

    print("\nEjecución finalizada\n")

    print("Mejor valor de aptitud encontrado:\n")

    print(mejor_aptitud)

    print("\nMejor distribución de sensores:\n")

    print(mejor_posicion)


    # Visualización de resultados
    print("\nGenerando visualizaciones...\n")

    visualizador = VisualizadorPSO(
        datos_procesados
    )

    visualizador.graficar_terreno_y_sensores(
        mejor_posicion,
        numero_sensores=10
    )

    visualizador.graficar_convergencia(
        enjambre.historial_aptitud
    )

if __name__ == "__main__":
    main()