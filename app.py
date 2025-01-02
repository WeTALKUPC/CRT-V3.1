import streamlit as st
import pandas as pd
import plotly.express as px

# Configurar el diseño en ancho completo
st.set_page_config(layout="wide")

# Título centrado de la aplicación
st.markdown(
    "<h1 style='text-align: center;'>Sistema de Seguimiento y Cumplimiento de Instructores (CRT)</h1>",
    unsafe_allow_html=True,
)

# URLs de los archivos Excel en GitHub (raw)
url_reemplazos = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx"
url_clases_totales = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202024%20V2.xlsx"

# Funciones para cargar los datos
@st.cache_data
def cargar_datos_reemplazos():
    try:
        data = pd.read_excel(url_reemplazos, engine="openpyxl")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo de reemplazos: {e}")
        return pd.DataFrame()

@st.cache_data
def cargar_datos_clases():
    try:
        data = pd.read_excel(url_clases_totales, engine="openpyxl")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo de clases totales: {e}")
        return pd.DataFrame()

# Cargar los datos
data_reemplazos = cargar_datos_reemplazos()
data_clases_totales = cargar_datos_clases()

# Verificar si los datos se cargaron correctamente
if not data_reemplazos.empty and not data_clases_totales.empty:
    # [FUNCIONALIDADES EXISTENTES - NO SE TOCAN]
    # (Mantener todo el código actual aquí)

    # NUEVA SECCIÓN: GRÁFICOS 2024
    st.subheader("Gráficos 2024")
    opciones_graficos = ["Seleccione un gráfico", "Reemplazos por Mes", "Reemplazos por Programa"]
    seleccion_grafico = st.selectbox("Selecciona un gráfico:", opciones_graficos)

    if seleccion_grafico == "Reemplazos por Mes":
        # Agregar columna de mes
        data_reemplazos["MES"] = data_reemplazos["FECHA DE CLASE"].dt.month
        reemplazos_por_mes = data_reemplazos["MES"].value_counts().sort_index()
        
        # Crear gráfico de barras
        fig_mes = px.bar(
            reemplazos_por_mes,
            x=reemplazos_por_mes.index,
            y=reemplazos_por_mes.values,
            labels={"x": "Mes", "y": "Cantidad de Reemplazos"},
            title="Reemplazos Atendidos por Mes en 2024",
        )
        st.plotly_chart(fig_mes, use_container_width=True)

    elif seleccion_grafico == "Reemplazos por Programa":
        # Contar reemplazos por programa
        reemplazos_por_programa = data_reemplazos["PROGRAMA"].value_counts()
        
        # Crear gráfico circular
        fig_programa = px.pie(
            reemplazos_por_programa,
            names=reemplazos_por_programa.index,
            values=reemplazos_por_programa.values,
            title="Reemplazos por Programa en 2024",
        )
        st.plotly_chart(fig_programa, use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos. Por favor, verifica los archivos.")
