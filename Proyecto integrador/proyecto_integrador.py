import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuración de página web
st.set_page_config(
    page_title="Auto Lavado Express La Estancia",
    page_icon="🧼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos visuales
st.markdown(
    """
    <style>
    .main-title { font-size: 2.2rem; color: #1E3A8A; font-weight: bold; margin-bottom: 0px; }
    .sub-title { font-size: 1.1rem; color: #4B5563; margin-bottom: 20px; }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown(
    '<div class="main-title">🧼 Auto Lavado Express La Estancia</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Sistema de Reporte Automatizado y Análisis de Ventas (Colima, Col.)</div>',
    unsafe_allow_html=True,
)

NOMBRE_ARCHIVO = "datos_autolavado.csv"
FECHA_INICIO_SISTEMA = datetime.strptime("2026-10-19", "%Y-%m-%d").date()


# Crear base de datos vacía con estructura si no existe
def inicializar_bd():
    if not os.path.exists(NOMBRE_ARCHIVO):
        df_base = pd.DataFrame(
            columns=[
                "id_servicio",
                "fecha_hora",
                "categoria_vehiculo",
                "tipo_lavado",
                "precio",
                "metodo_pago",
                "lavador",
                "duracion_minutos",
            ]
        )
        df_base.to_csv(NOMBRE_ARCHIVO, index=False)


inicializar_bd()


@st.cache_data(ttl=2)
def cargar_datos():
    try:
        df_data = pd.read_csv(NOMBRE_ARCHIVO)
        if not df_data.empty:
            df_data["fecha_hora"] = pd.to_datetime(df_data["fecha_hora"])
            df_data["fecha"] = df_data["fecha_hora"].dt.date
            df_data["hora"] = df_data["fecha_hora"].dt.hour
            df_data["dia_semana"] = df_data["fecha_hora"].dt.day_name()
            # Filtrar solo registros a partir del inicio de operaciones (19 de octubre de 2026)
            df_data = df_data[df_data["fecha"] >= FECHA_INICIO_SISTEMA]
        return df_data
    except Exception:
        return pd.DataFrame()


df = cargar_datos()

# ---------------------------------------------------------
# SIDEBAR: REGISTRO DIRECTO Y FILTROS
# ---------------------------------------------------------
st.sidebar.header("📝 Registro Manual (Respaldo en Caja)")

CAT_PRECIOS = {
    "Carro (Pequeño/Mediano) - Normal": (
        "Carro (Pequeño/Mediano)",
        "Normal",
        90.0,
    ),
    "Carro (Pequeño/Mediano) - Con brillo y cera": (
        "Carro (Pequeño/Mediano)",
        "Con brillo y cera",
        110.0,
    ),
    "Camioneta (Mediana/Grande) - Normal": (
        "Camioneta (Mediana/Grande)",
        "Normal",
        110.0,
    ),
    "Camioneta (Mediana/Grande) - Con brillo y cera": (
        "Camioneta (Mediana/Grande)",
        "Con brillo y cera",
        130.0,
    ),
    "Moto - Normal": ("Moto", "Normal", 70.0),
    "Moto - Con brillo y cera": ("Moto", "Con brillo y cera", 100.0),
    "Benz Pasajeros - Normal": ("Benz Pasajeros", "Normal", 110.0),
    "Cuatrimoto - Con brillo y cera": (
        "Cuatrimoto",
        "Con brillo y cera",
        350.0,
    ),
    "Razer - Con brillo y cera": ("Razer", "Con brillo y cera", 500.0),
    "Taxi - Normal": ("Taxi", "Normal", 60.0),
}

with st.sidebar.form("form_registro", clear_on_submit=True):
    opcion_servicio = st.selectbox(
        "Servicio y Tarifa", list(CAT_PRECIOS.keys())
    )
    lavador_reg = st.selectbox(
        "Lavador", ["Carlos", "Juan", "Pedro", "Luis", "Miguel"]
    )
    metodo_reg = st.selectbox(
        "Método de Pago", ["Efectivo", "Tarjeta", "Transferencia"]
    )
    duracion_reg = st.number_input(
        "Duración (min)", min_value=10, max_value=120, value=25
    )

    btn_guardar = st.form_submit_button("💾 Registrar Lavado")

    if btn_guardar:
        ahora = datetime.now()
        hora_actual = ahora.hour
        dia_actual = ahora.weekday()  # 0=Lunes, 6=Domingo

        # Validación de horarios reales
        # Lunes a Sábado: 8am a 7pm (8 a 19) | Domingos: 8am a 2pm (8 a 14)
        abierto = False
        if dia_actual < 6 and 8 <= hora_actual < 19:
            abierto = True
        elif dia_actual == 6 and 8 <= hora_actual < 14:
            abierto = True

        if not abierto:
            st.warning(
                "⚠️ Advertencia: Registro fuera del horario oficial de La Estancia (Lun-Sáb: 8am-7pm | Dom: 8am-2pm)."
            )

        cat_sel, tipo_sel, precio_sel = CAT_PRECIOS[opcion_servicio]
        df_actual = pd.read_csv(NOMBRE_ARCHIVO)
        nuevo_id = f"LAV-{(len(df_actual) + 1):04d}"

        nuevo_registro = pd.DataFrame(
            [
                {
                    "id_servicio": nuevo_id,
                    "fecha_hora": ahora.strftime("%Y-%m-%d %H:%M:%S"),
                    "categoria_vehiculo": cat_sel,
                    "tipo_lavado": tipo_sel,
                    "precio": precio_sel,
                    "metodo_pago": metodo_reg,
                    "lavador": lavador_reg,
                    "duracion_minutos": duracion_reg,
                }
            ]
        )

        df_actual = pd.concat([df_actual, nuevo_registro], ignore_index=True)
        df_actual.to_csv(NOMBRE_ARCHIVO, index=False)
        st.success(
            f"✅ Lavado {nuevo_id} registrado exitosamente (${precio_sel:.2f})."
        )
        st.cache_data.clear()
        st.rerun()

st.sidebar.divider()
st.sidebar.header("🔍 Filtros de Reportes")

if not df.empty:
    min_fecha = max(df["fecha"].min(), FECHA_INICIO_SISTEMA)
    max_fecha = df["fecha"].max()

    rango_fechas = st.sidebar.date_input(
        "Rango de Fechas",
        value=(min_fecha, max_fecha),
        min_value=FECHA_INICIO_SISTEMA,
    )

    lavadores_disp = df["lavador"].unique() if "lavador" in df.columns else []
    sel_lavador = st.sidebar.multiselect(
        "Lavador", options=lavadores_disp, default=lavadores_disp
    )

    metodos_disp = (
        df["metodo_pago"].unique() if "metodo_pago" in df.columns else []
    )
    sel_metodo = st.sidebar.multiselect(
        "Método de Pago", options=metodos_disp, default=metodos_disp
    )

    if isinstance(rango_fechas, tuple) and len(rango_fechas) == 2:
        f_inicio, f_fin = rango_fechas
        mask = (
            (df["fecha"] >= f_inicio)
            & (df["fecha"] <= f_fin)
            & (df["lavador"].isin(sel_lavador))
            & (df["metodo_pago"].isin(sel_metodo))
        )
        df_filtrado = df[mask]
    else:
        df_filtrado = df
else:
    df_filtrado = df

if st.sidebar.button("🔄 Actualizar Datos"):
    st.cache_data.clear()
    st.rerun()

# ---------------------------------------------------------
# CONTENIDO PRINCIPAL: VISUALIZACIÓN DE DATOS (ROMÁN)
# ---------------------------------------------------------
if df_filtrado.empty:
    st.info(
        "ℹ️ No hay servicios registrados a partir del inicio de operaciones (19 de octubre de 2026)."
    )
    st.markdown(
        "Regístralos usando el formulario de la izquierda o mediante la app de Antigravity."
    )
else:
    # Métricas / KPIs reales
    ingreso_total = df_filtrado["precio"].sum()
    cantidad_lavados = len(df_filtrado)
    ticket_promedio = (
        df_filtrado["precio"].mean() if cantidad_lavados > 0 else 0.0
    )
    tiempo_promedio = (
        df_filtrado["duracion_minutos"].mean() if cantidad_lavados > 0 else 0.0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ingresos Totales", f"${ingreso_total:,.2f} MXN")
    col2.metric("Total de Lavados", f"{cantidad_lavados}")
    col3.metric("Ticket Promedio", f"${ticket_promedio:,.2f} MXN")
    col4.metric("Tiempo Promedio", f"{tiempo_promedio:.0f} min")

    st.divider()

    # Gráficos Unidad 2
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("1. Ingresos por Categoría de Vehículo")
        ing_cat = (
            df_filtrado.groupby("categoria_vehiculo")["precio"]
            .sum()
            .reset_index()
            .sort_values(by="precio", ascending=False)
        )
        fig_cat = px.bar(
            ing_cat,
            x="precio",
            y="categoria_vehiculo",
            orientation="h",
            text_auto="$.2f",
            labels={"precio": "Ingresos ($)", "categoria_vehiculo": "Categoría"},
            color="precio",
            color_continuous_scale="Blues",
        )
        fig_cat.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_cat, use_container_width=True)

    with c2:
        st.subheader("2. Distribución de Tipos de Servicio")
        pref_serv = df_filtrado["tipo_lavado"].value_counts().reset_index()
        fig_pie = px.pie(
            pref_serv,
            values="count",
            names="tipo_lavado",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_layout(height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("3. Rendimiento por Lavador")
        prod_lav = (
            df_filtrado.groupby("lavador")["precio"]
            .agg(["sum", "count"])
            .reset_index()
        )
        fig_lav = px.bar(
            prod_lav,
            x="lavador",
            y="sum",
            text="count",
            labels={
                "sum": "Generado ($)",
                "lavador": "Lavador",
                "count": "Autos",
            },
            color="sum",
            color_continuous_scale="Viridis",
        )
        fig_lav.update_traces(
            texttemplate="%{text} lavados", textposition="outside"
        )
        fig_lav.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_lav, use_container_width=True)

    with c4:
        st.subheader("4. Horas Pico de Atención (Afluencia)")
        horas_pico = (
            df_filtrado.groupby("hora")["id_servicio"].count().reset_index()
        )
        fig_hora = px.line(
            horas_pico,
            x="hora",
            y="id_servicio",
            markers=True,
            labels={
                "hora": "Hora del Día (24 hrs)",
                "id_servicio": "Cantidad de Lavados",
            },
        )
        fig_hora.update_layout(height=350)
        st.plotly_chart(fig_hora, use_container_width=True)

    st.divider()

    # Tabla y descarga
    st.subheader("📋 Transacciones Registradas")
    st.dataframe(df_filtrado, use_container_width=True)

    csv_data = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar Reporte Completo (CSV)",
        data=csv_data,
        file_name="reporte_autolavado_la_estancia.csv",
        mime="text/csv",
    )