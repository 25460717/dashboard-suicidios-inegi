import os
import pandas as pd

# Nombre del archivo que utiliza la aplicación de Streamlit
NOMBRE_ARCHIVO = "datos_autolavado.csv"


def crear_base_datos_limpia():
    # Definición de las columnas que Mónico y Antigravity enviarpan al pipeline
    columnas = [
        "id_servicio",
        "fecha_hora",
        "categoria_vehiculo",
        "tipo_lavado",
        "precio",
        "metodo_pago",
        "lavador",
        "duracion_minutos",
    ]

    # Crear DataFrame vacío con las cabeceras oficiales
    df_vacio = pd.DataFrame(columns=columnas)

    # Guardar en formato CSV
    df_vacio.to_csv(NOMBRE_ARCHIVO, index=False)
    print(
        f"✅ Archivo '{NOMBRE_ARCHIVO}' creado con éxito. Base de datos lista para arrancar mañana lunes 19 de octubre de 2026."
    )


if __name__ == "__main__":
    crear_base_datos_limpia()