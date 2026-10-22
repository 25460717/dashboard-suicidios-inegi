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

# Estilos CSS avanzados para un aspecto "Executive/Premium"
st.markdown("""
    <style>
    /* Estilo para las tarjetas de KPI personalizadas */
    .kpi-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #A0AEC0;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 20px;
        font-weight: 700;
        color: #3182CE;
        line-height: 1.2;
    }
    .kpi-subtext {
        font-size: 11px;
        color: #718096;
        margin-top: 4px;
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
# 3. KPIS PRINCIPALES CON TARJETAS PREMIUM
# ==============================================================================
col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

total_defunciones = df_filtrado["Defunciones"].sum()

if not df_filtrado.empty and total_defunciones > 0:
    top_causa = df_filtrado.groupby("Causa")["Defunciones"].sum().idxmax()
    porcentaje_hombres = (
        df_filtrado[df_filtrado["Sexo"] == "Hombres"]["Defunciones"].sum() / total_defunciones * 100
    )
    promedio_anual = total_defunciones / len(anio_sel) if len(anio_sel) > 0 else 0
else:
    top_causa = "Sin datos"
    porcentaje_hombres = 0
    promedio_anual = 0

with col_kpi1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📊 Total Registrado</div>
            <div class="kpi-value">{total_defunciones} casos</div>
            <div class="kpi-subtext">Periodo seleccionado</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi2:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">⚠️ Causa Principal</div>
            <div class="kpi-value">{top_causa}</div>
            <div class="kpi-subtext">Mayor número de incidencias</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi3:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">👨 Proporción Hombres</div>
            <div class="kpi-value">{porcentaje_hombres:.1f}%</div>
            <div class="kpi-subtext">Del total de casos</div>
        </div>
    """, unsafe_allow_html=True)

with col_kpi4:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">📅 Promedio Anual</div>
            <div class="kpi-value">{promedio_anual:.1f} casos/año</div>
            <div class="kpi-subtext">Frecuencia por año</div>
        </div>
    """, unsafe_allow_html=True)

st.divider()


# ==============================================================================
# 4. PESTAÑAS Y GRÁFICOS INTERACTIVOS
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
