import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Suicidios INEGI", page_icon="🧠", layout="wide"
)


# ==============================================================================
# 1. CAPA DE BACKEND: CARGA Y LIMPIEZA DE DATOS CON @st.cache_data
# ==============================================================================
@st.cache_data
def cargar_y_limpiar_datos(filepath: str) -> pd.DataFrame:
    """Carga el archivo Excel del INEGI, procesa su estructura matricial

    y la transforma en un DataFrame tabular limpio.
    """
    df_raw = pd.read_excel(filepath, header=None)

    # Extraer años (Fila index 6) y sexos (Fila index 7)
    years = df_raw.iloc[6].values
    sexes = df_raw.iloc[7].values

    # Filas con los datos de las causas (Filas 8 a 12)
    data_rows = df_raw.iloc[8:13].copy()

    records = []
    for _, row in data_rows.iterrows():
        entidad = str(row[0]).strip() if pd.notnull(row[0]) else "Desconocido"
        causa = str(row[1]).strip() if pd.notnull(row[1]) else "Desconocido"

        for col_idx in range(2, len(row)):
            year = years[col_idx]
            sex = str(sexes[col_idx]).strip()
            val = row[col_idx]

            records.append({
                "Entidad": entidad,
                "Causa": causa,
                "Año": int(year),
                "Sexo": sex,
                "Defunciones": int(val) if pd.notnull(val) else 0,
            })

    return pd.DataFrame(records)


# Búsqueda flexible del archivo para evitar errores de ruta (FileNotFoundError)
posibles_rutas = [
    "Mental_07 (1).xlsx",
    "../Mental_07 (1).xlsx",
    "Mental_07.xlsx",
    "../Mental_07.xlsx",
]

archivo_encontrado = None
for ruta in posibles_rutas:
    if os.path.exists(ruta):
        archivo_encontrado = ruta
        break

if archivo_encontrado:
    df_raw = cargar_y_limpiar_datos(archivo_encontrado)
else:
    st.error(
        "❌ No se encontró el archivo Excel 'Mental_07 (1).xlsx'. Verifica que esté dentro de la carpeta del proyecto."
    )
    st.stop()


# ==============================================================================
# 2. CAPA DE FRONTEND: WIDGETS Y FILTROS INTERACTIVOS
# ==============================================================================
st.title("🧠 Dashboard de Defunciones por Suicidio (INEGI)")
st.sidebar.header("Filtros de Control")

# Widget 1: Selección de Año (Multiselect)
anios_disponibles = sorted(df_raw["Año"].unique().tolist())
anio_sel = st.sidebar.multiselect(
    "Selecciona el Año:",
    options=anios_disponibles,
    default=anios_disponibles,
)

# Widget 2: Selección de Causa (Multiselect)
causas_disponibles = [c for c in df_raw["Causa"].unique() if c != "Total"]
causa_sel = st.sidebar.multiselect(
    "Selecciona la Causa:",
    options=causas_disponibles,
    default=causas_disponibles,
)

# Aplicar filtros al DataFrame
df_filtrado = df_raw[
    (df_raw["Año"].isin(anio_sel))
    & (df_raw["Causa"].isin(causa_sel))
    & (df_raw["Sexo"] != "Total")
]


# ==============================================================================
# 3. CAPA DE FRONTEND: KPIS Y GRÁFICOS INTERACTIVOS (PLOTLY)
# ==============================================================================
col1, col2 = st.columns(2)

total_defunciones = df_filtrado["Defunciones"].sum()
col1.metric("Total Registrado", f"{total_defunciones} casos")

if not df_filtrado.empty and total_defunciones > 0:
    top_causa = df_filtrado.groupby("Causa")["Defunciones"].sum().idxmax()
    col2.metric("Causa con Mayor Incidencia", top_causa)
else:
    col2.metric("Causa con Mayor Incidencia", "Sin datos")

st.divider()

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Distribución por Causa y Sexo")
    fig_bar = px.bar(
        df_filtrado,
        x="Causa",
        y="Defunciones",
        color="Sexo",
        barmode="group",
        labels={"Defunciones": "Casos", "Causa": "Causa de Defunción"},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_g2:
    st.subheader("Tendencia Temporal por Año")
    df_tendencia = df_filtrado.groupby("Año")["Defunciones"].sum().reset_index()
    fig_line = px.line(
        df_tendencia,
        x="Año",
        y="Defunciones",
        markers=True,
        labels={"Defunciones": "Total Casos"},
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Vista desplegable de la tabla de datos procesados
with st.expander("📄 Ver Datos Filtrados"):
    st.dataframe(df_filtrado, use_container_width=True)