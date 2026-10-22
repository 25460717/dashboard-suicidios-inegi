import os
import pandas as pd
import plotly.express as px
import streamlit as st

# ==============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Suicidios INEGI",
    page_icon="🧠",
    layout="wide"
)

# Mapa de colores unificado para mantener consistencia visual
COLOR_DISCRETE_MAP = {
    "Hombres": "#2B5C8F",
    "Mujeres": "#D95D39",
    "No especificado": "#8D99AE"
}

# ==============================================================================
# 1. CAPA DE BACKEND: CARGA Y LIMPIEZA DE DATOS
# ==============================================================================
@st.cache_data
def cargar_y_limpiar_datos(filepath: str) -> pd.DataFrame:
    df_excel = pd.read_excel(filepath, header=None)

    years = df_excel.iloc[6].values
    sexes = df_excel.iloc[7].values
    data_rows = df_excel.iloc[8:13].copy()

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


posibles_rutas = [
    "Mental_07 (1).xlsx",
    "Actividades/Mental_07 (1).xlsx",
    "Mental_07.xlsx",
    "Actividades/Mental_07.xlsx"
]

archivo_encontrado = None
for ruta in posibles_rutas:
    if os.path.exists(ruta):
        archivo_encontrado = ruta
        break

if archivo_encontrado is not None:
    df_datos = cargar_y_limpiar_datos(archivo_encontrado)
else:
    st.error("❌ No se encontró el archivo 'Mental_07 (1).xlsx'. Verifica la raíz del repositorio.")
    st.stop()


# ==============================================================================
# 2. CAPA DE FRONTEND: FILTROS Y JERARQUÍA VISUAL
# ==============================================================================
st.title("🧠 Dashboard de Defunciones por Suicidio (INEGI)")
st.markdown("### **Análisis de datos registrados en Colima (2019 - 2021)**")
st.caption("Herramienta interactiva para el análisis de causa de defunción por género y tendencia temporal.")

# Filtros en la barra lateral
st.sidebar.header("Filtros de Control")

anios_disponibles = sorted(df_datos["Año"].unique().tolist())
anio_sel = st.sidebar.multiselect(
    "Selecciona el Año:",
    options=anios_disponibles,
    default=anios_disponibles,
)

causas_disponibles = [c for c in df_datos["Causa"].unique() if c != "Total"]
causa_sel = st.sidebar.multiselect(
    "Selecciona la Causa:",
    options=causas_disponibles,
    default=causas_disponibles,
)

# Filtrado de datos
df_filtrado = df_datos[
    (df_datos["Año"].isin(anio_sel))
    & (df_datos["Causa"].isin(causa_sel))
    & (df_datos["Sexo"] != "Total")
]


# ==============================================================================
# 3. METRICAS / KPIS PRINCIPALES (JERARQUÍA VISUAL MÁS ALTA)
# ==============================================================================
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

total_defunciones = df_filtrado["Defunciones"].sum()
col_kpi1.metric("Total Registrado", f"{total_defunciones} casos")

if not df_filtrado.empty and total_defunciones > 0:
    top_causa = df_filtrado.groupby("Causa")["Defunciones"].sum().idxmax()
    col_kpi2.metric("Causa Principal", top_causa)
    
    porcentaje_hombres = (
        df_filtrado[df_filtrado["Sexo"] == "Hombres"]["Defunciones"].sum() / total_defunciones * 100
    )
    col_kpi3.metric("Proporción Hombres", f"{porcentaje_hombres:.1f}%")
else:
    col_kpi2.metric("Causa Principal", "Sin datos")
    col_kpi3.metric("Proporción Hombres", "0%")

st.divider()


# ==============================================================================
# 4. GRÁFICOS Y INSIGHTS DE APOYO
# ==============================================================================
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("1. Distribución por Causa y Sexo")
    fig_bar = px.bar(
        df_filtrado,
        x="Causa",
        y="Defunciones",
        color="Sexo",
        barmode="group",
        labels={"Defunciones": "Número de Casos", "Causa": "Causa Registrada", "Sexo": "Género"},
        color_discrete_map=COLOR_DISCRETE_MAP,
    )
    fig_bar.update_layout(
        xaxis_title="Causa de Defunción",
        yaxis_title="Número de Casos",
        legend_title_text="Género"
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Texto de apoyo con insight clave (Punto 3)
    st.caption("📌 **Insight:** El ahorcamiento, estrangulamiento o sofocación representa la causa predominante en la entidad, registrando un volumen considerablemente superior en la población masculina.")

with col_g2:
    st.subheader("2. Evolución Temporal del Periodo")
    df_tendencia = df_filtrado.groupby(["Año", "Sexo"])["Defunciones"].sum().reset_index()
    fig_line = px.line(
        df_tendencia,
        x="Año",
        y="Defunciones",
        color="Sexo",
        markers=True,
        labels={"Defunciones": "Número de Casos", "Año": "Año de Registro", "Sexo": "Género"},
        color_discrete_map=COLOR_DISCRETE_MAP,
    )
    fig_line.update_layout(
        xaxis=dict(tickmode='linear', tick0=2019, dtick=1),
        xaxis_title="Año de Registro",
        yaxis_title="Número de Casos",
        legend_title_text="Género"
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Texto de apoyo con insight clave (Punto 3)
    st.caption("📌 **Insight:** La tendencia histórica muestra una brecha persistente entre géneros, permitiendo identificar variaciones anuales en los registros totales de la región.")

st.markdown("---")
st.caption("Fuente de datos: Instituto Nacional de Estadística y Geografía (INEGI) — Registros de Mortalidad en Colima.")

# Tabla de datos
with st.expander("📄 Ver Datos Registrados (Tabla Completa)"):
    st.dataframe(df_filtrado, use_container_width=True)
