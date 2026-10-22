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
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para permitir texto completo y dinámico en las tarjetas KPI
st.markdown("""
    <style>
    /* Ajusta el tamaño del texto del KPI para que no se recorte */
    [data-testid="stMetricValue"] {
        font-size: 18px !important;
        font-weight: bold;
        color: #1E88E5;
        white-space: normal !important;
        word-wrap: break-word !important;
        line-height: 1.3;
    }
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# Mapa de colores unificado
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
# 2. CAPA DE FRONTEND: FILTROS Y BARRA LATERAL
# ==============================================================================
st.title("🧠 Dashboard de Defunciones por Suicidio (INEGI)")
st.markdown("### **Análisis de Mortalidad en Colima (2019 - 2021)**")
st.caption("Visualización interactiva e inteligibilidad de datos para la toma de decisiones en salud pública.")

st.sidebar.header("⚙️ Filtros de Control")

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
# 3. KPIS PRINCIPALES DE IMPACTO (TEXTOS COMPLETOS)
# ==============================================================================
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

total_defunciones = df_filtrado["Defunciones"].sum()
col_kpi1.metric("Total Registrado", f"{total_defunciones} casos")

if not df_filtrado.empty and total_defunciones > 0:
    top_causa = df_filtrado.groupby("Causa")["Defunciones"].sum().idxmax()
    col_kpi2.metric("Causa Principal", top_causa)
    
    porcentaje_hombres = (
        df_filtrado[df_filtrado["Sexo"] == "Hombres"]["Defunciones"].sum() / total_defunciones * 100
    )
    col_kpi3.metric("Proporción Hombres", f"{porcentaje_hombres:.1f}%")
    
    promedio_anual = total_defunciones / len(anio_sel) if len(anio_sel) > 0 else 0
    col_kpi4.metric("Promedio Anual", f"{promedio_anual:.1f} casos/año")
else:
    col_kpi2.metric("Causa Principal", "Sin datos")
    col_kpi3.metric("Proporción Hombres", "0%")
    col_kpi4.metric("Promedio Anual", "0 casos")

st.divider()


# ==============================================================================
# 4. ESTRUCTURA EN PESTAÑAS (TABS) PARA MEJOR NAVEGACIÓN
# ==============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Vista General", "📈 Tendencias Temporales", "📄 Datos Detallados"])

with tab1:
    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.subheader("Distribución por Causa y Sexo")
        fig_bar = px.bar(
            df_filtrado,
            x="Causa",
            y="Defunciones",
            color="Sexo",
            barmode="group",
            text_auto=True,
            labels={"Defunciones": "Número de Casos", "Causa": "Causa Registrada", "Sexo": "Género"},
            color_discrete_map=COLOR_DISCRETE_MAP,
        )
        fig_bar.update_layout(
            xaxis_title="Causa de Defunción",
            yaxis_title="Número de Casos",
            legend_title_text="Género"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.caption("📌 **Insight:** La asfixia por ahorcamiento representa el porcentaje mayoritario de los casos registrados, afectando en mayor proporción a los hombres.")

    with col_g2:
        st.subheader("Proporción de Casos por Género")
        df_sexo = df_filtrado.groupby("Sexo")["Defunciones"].sum().reset_index()
        fig_pie = px.pie(
            df_sexo,
            values="Defunciones",
            names="Sexo",
            hole=0.4,
            color="Sexo",
            color_discrete_map=COLOR_DISCRETE_MAP
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        st.caption("📌 **Insight:** La brecha de género es notablemente amplia, con más del 80% de los registros concentrados en la población masculina.")

with tab2:
    st.subheader("Evolución Temporal del Periodo")
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
    st.caption("📌 **Insight:** Durante el periodo 2019-2021 se observa un incremento sostenido en la tendencia anual, especialmente en la incidencia masculina.")

with tab3:
    st.subheader("Registro de Datos Procesados")
    st.dataframe(df_filtrado, use_container_width=True)
    
    # Botón de descarga CSV
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar datos filtrados en CSV",
        data=csv,
        file_name='datos_suicidios_colima.csv',
        mime='text/csv',
    )

st.markdown("---")
st.caption("Fuente de datos: Instituto Nacional de Estadística y Geografía (INEGI) — Registros de Mortalidad en Colima.")
