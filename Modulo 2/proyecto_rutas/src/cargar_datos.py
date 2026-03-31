# cargar_datos.py
from pathlib import Path        # para manipular las rutas de los archivos
import pandas as pd             # para manipular datos en forma de tablas (por ejemplo Excel)

""" 
Cada función sera utilizada en el modulo principal,
donde a partir de rutas definidas se realizara la carga de
los archivos especificados.
"""

# Carga el archivo Excel con los datos de centros de distribución y tiendas
def cargar_archivo_distribucion(ruta_archivo: str | Path) -> pd.DataFrame:
    ruta_archivo = Path(ruta_archivo)
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    return pd.read_excel(ruta_archivo)


# Carga una matriz Excel de distancias entre nodos (tiendas y centros de distribución)
def cargar_matriz(ruta_archivo: str | Path) -> pd.DataFrame:
    ruta_archivo = Path(ruta_archivo)
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    return pd.read_excel(ruta_archivo)


# Agrega la columna ID_Nodo para trabajar con identificadores numéricos
def preparar_datos_problema(datos: pd.DataFrame) -> pd.DataFrame:
    datos = datos.copy()
    datos["ID_Nodo"] = range(1, len(datos) + 1)
    return datos


# Se separan los nodos en centros de distribución y tiendas
def obtener_centros_y_tiendas(datos: pd.DataFrame) -> tuple[list[int], list[int]]:
    centros = datos.loc[datos["Tipo"] == "Centro de Distribución", "ID_Nodo"].tolist()
    tiendas = datos.loc[datos["Tipo"] != "Centro de Distribución", "ID_Nodo"].tolist()
    return centros, tiendas


# Genera un diccionario que relaciona ID_Nodo con el nombre real del nodo
# Útil para la presentación de resultados
def obtener_nombre_por_id(datos: pd.DataFrame) -> dict[int, str]:
    return dict(zip(datos["ID_Nodo"], datos["Nombre"]))


# Genera un diccionario que relaciona ID_Nodo con la zona del nodo
# La columna zona fue agregada con la función auxiliar al momento de crear el mapa de ubicaciones
def obtener_zona_por_id(datos: pd.DataFrame) -> dict[int, str]:
    if "Zona" not in datos.columns:
        return {}
    return dict(zip(datos["ID_Nodo"], datos["Zona"]))
