import streamlit as st
import pandas as pd
import plotly.express as px

# Título de la aplicación
st.title("Dashboard de Cumplimiento por Feriado, Programa e Instructor")

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
    # Contar reemplazos realizados por cada instructor titular
    reemplazos_contados = data_reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")

    # Cruzar los datos con el archivo de clases totales
    data_combinada = pd.merge(data_clases_totales, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")

    # Rellenar NaN en "REEMPLAZOS REALIZADOS" con 0 para instructores sin reemplazos
    data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)

    # Calcular el porcentaje de cumplimiento
    data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada["CLASES TOTALES 2024"]) * 100

    # Crear un diccionario para relacionar nombres y usuarios
    usuarios_a_nombres = dict(zip(data_combinada["USUARIO INSTRUCTOR TITULAR"], data_combinada["NOMBRE INSTRUCTOR"]))

    # Crear filtros
    st.subheader("Filtros de Búsqueda")

    # Filtro de instructor titular con nombres visibles
    nombres_instructores = ["Seleccione un instructor"] + sorted(data_combinada["NOMBRE INSTRUCTOR"].dropna().unique().tolist())
    seleccion_nombre = st.selectbox("Selecciona un instructor titular:", nombres_instructores)

    # Obtener el usuario del instructor seleccionado
    if seleccion_nombre != "Seleccione un instructor":
        usuario_seleccionado = {v: k for k, v in usuarios_a_nombres.items()}.get(seleccion_nombre)

        # Filtrar los datos para el instructor seleccionado
        datos_instructor = data_combinada[data_combinada["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]

        # Mostrar los datos filtrados del instructor
        st.subheader(f"Cumplimiento Anual del Instructor: {seleccion_nombre}")
        st.dataframe(datos_instructor)

        # Crear gráfico circular del cumplimiento anual
        reemplazos = datos_instructor["REEMPLAZOS REALIZADOS"].iloc[0]
        cumplimiento = datos_instructor["CLASES TOTALES 2024"].iloc[0] - reemplazos
        fig = px.pie(
            names=["Clases Cumplidas", "Reemplazos Realizados"],
            values=[cumplimiento, reemplazos],
            title=f"Cumplimiento Anual de {seleccion_nombre}"
        )
        st.plotly_chart(fig)

else:
    st.warning("No se pudieron cargar los datos. Por favor, verifica los archivos.")
