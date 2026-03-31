# generar_mapa.py
# modulo auxiliar
from pathlib import Path
import folium
import pandas as pd


# RUTAS DEL PROYECTO
# Carpeta raíz del proyecto.
DIRECTORIO_BASE = Path(__file__).resolve().parent.parent

# Archivo original con la información de centros y tiendas.
ARCHIVO_ENTRADA = DIRECTORIO_BASE / "data" / "datos_distribucion_tiendas.xlsx"

# Archivo modificado con la nueva columna de zona.
ARCHIVO_SALIDA_EXCEL = DIRECTORIO_BASE / "data" / "datos_distribucion_tiendas_con_zona.xlsx"

# Mapa HTML generado.
ARCHIVO_SALIDA_HTML = DIRECTORIO_BASE / "results" / "mapa_centros_tiendas_por_zona.html"



# FUNCIÓN AUXILIAR
"""
Asigna una zona geográfica a cada nodo usando el punto medio del conjunto de coordenadas.

La asignación se hace con base en dos puntos:
    - latitud_media
    - longitud_media

Se divide en 4 zonas:
    - Noreste
    - Noroeste
    - Sureste
    - Suroeste
"""
def asignar_zona(latitud: float, longitud: float, latitud_media: float, longitud_media: float) -> str:
    if latitud >= latitud_media and longitud >= longitud_media:
        return "Noreste"
    elif latitud >= latitud_media and longitud < longitud_media:
        return "Noroeste"
    elif latitud < latitud_media and longitud >= longitud_media:
        return "Sureste"
    else:
        return "Suroeste"


# FUNCIÓN PARA CREAR MAPA HTML
"""
Un mapa HTML usando Folium.
Cada nodo se pinta según su zona regional y se separa además
entre centro de distribución y tienda.
"""
def crear_mapa(datos: pd.DataFrame, archivo_html: Path) -> None:
    # Colores asignados a cada zona regional.
    colores_zona = {
        "Noreste": "#ff7f0e",    # rojo
        "Noroeste": "#1f77b4",  # azul
        "Sureste": "#d62728",    # verde
        "Suroeste": "#2ca02c",  # naranja
    }

    # Se calcula el centro del mapa usando el promedio de coordenadas.
    latitud_centro = datos["Latitud_WGS84"].mean()
    longitud_centro = datos["Longitud_WGS84"].mean()

    # Se crea el mapa base.
    mapa = folium.Map(
        location=[latitud_centro, longitud_centro],
        zoom_start=12,
        tiles="OpenStreetMap",
    )
    
    for _, fila in datos.iterrows():
        zona = fila["Zona"]
        color_relleno = colores_zona.get(zona, "#666666")
        es_centro = fila["Tipo"] == "Centro de Distribución"

        # El contorno negro solo se aplica a los centros.
        if es_centro:
            color_contorno = "black"
            grosor_contorno = 1
            radio = 6
            opacidad_relleno = 0.95
        else:
            color_contorno = color_relleno
            grosor_contorno = 1.5
            radio = 6
            opacidad_relleno = 0.75

        # Contenido al hacer clic en el marcador.
        contenido_popup = f"""
        <div style="font-size: 13px;">
            <b>{fila['Nombre']}</b><br>
            <b>Tipo:</b> {fila['Tipo']}<br>
            <b>Zona:</b> {zona}<br>
            <b>Latitud:</b> {fila['Latitud_WGS84']:.6f}<br>
            <b>Longitud:</b> {fila['Longitud_WGS84']:.6f}
        </div>
        """

        # Se agrega el nodo al mapa.
        folium.CircleMarker(
            location=[fila["Latitud_WGS84"], fila["Longitud_WGS84"]],
            radius=radio,
            popup=folium.Popup(contenido_popup, max_width=300),
            tooltip=f"{fila['Nombre']} | {zona}",
            color=color_contorno,
            weight=grosor_contorno,
            fill=True,
            fill_color=color_relleno,
            fill_opacity=opacidad_relleno,
        ).add_to(mapa)

    # Ajustar el mapa a la extensión de todos los nodos.
    mapa.fit_bounds(datos[["Latitud_WGS84", "Longitud_WGS84"]].values.tolist())

    # Guardar el archivo HTML final.
    archivo_html.parent.mkdir(parents=True, exist_ok=True)
    mapa.save(archivo_html)

# FUNCIÓN PRINCIPAL
"""
Función principal
Acciones que realiza:
    - Lee el archivo original de distribución de tiendas.
    - Calcula la zona geográfica de cada nodo.
    - Guarda un archivo Excel modificado con la nueva columna de zona.
    - Genera el mapa HTML.
"""
def main() -> None:
    if not ARCHIVO_ENTRADA.exists():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {ARCHIVO_ENTRADA}")

    datos = pd.read_excel(ARCHIVO_ENTRADA)

    columnas_necesarias = {"Tipo", "Nombre", "Latitud_WGS84", "Longitud_WGS84"}
    columnas_faltantes = columnas_necesarias - set(datos.columns)

    if columnas_faltantes:
        raise ValueError(f"Faltan columnas requeridas en el Excel: {columnas_faltantes}")

    # Calcular la mediana de las coordenadas.
    # Se usa como referencia para dividir el plano geográfico en 4 zonas.
    latitud_media = datos["Latitud_WGS84"].median()
    longitud_media = datos["Longitud_WGS84"].median()

    # Agregar la columna "Zona" si todavía no existe.
    if "Zona" not in datos.columns:
        datos["Zona"] = datos.apply(
            lambda fila: asignar_zona(
                fila["Latitud_WGS84"],
                fila["Longitud_WGS84"],
                latitud_media,
                longitud_media,
            ),
            axis=1,
        )

    ARCHIVO_SALIDA_EXCEL.parent.mkdir(parents=True, exist_ok=True)
    datos.to_excel(ARCHIVO_SALIDA_EXCEL, index=False)

    # Generar el mapa HTML.
    crear_mapa(datos, ARCHIVO_SALIDA_HTML)

    print("Archivo Excel modificado guardado en:", ARCHIVO_SALIDA_EXCEL)
    print("Mapa HTML guardado en:", ARCHIVO_SALIDA_HTML)


if __name__ == "__main__":
    main()