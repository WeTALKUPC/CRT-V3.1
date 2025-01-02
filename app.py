import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Dashboard de Cumplimiento por Feriado, Programa e Instructor")

# URLs de los archivos Excel en GitHub (raw)
url_reemplazos = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx"
url_clases_totales = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202024%20V2.xlsx"

# Función para cargar los datos
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

# Verificar si el archivo de reemplazos se cargó correctamente
if not data_reemplazos.empty:
    # Crear los filtros
    st.subheader("Filtros de Búsqueda")

    # Filtro de instructor titular
    instructores = ["TODOS"] + sorted(data_reemplazos["INSTRUCTOR TITULAR"].dropna().unique().tolist())
    seleccion_instructor = st.selectbox("Selecciona un instructor titular:", instructores)

    # Filtro de motivo de reemplazo
    motivos = ["TODOS"] + sorted(data_reemplazos["MOTIVO DE REEMPLAZO"].dropna().unique().tolist())
    seleccion_motivo = st.selectbox("Selecciona un motivo de reemplazo:", motivos)

    # Filtrar los datos según la selección
    data_filtrada = data_reemplazos.copy()
    
    if seleccion_instructor != "TODOS":
        data_filtrada = data_filtrada[data_filtrada["INSTRUCTOR TITULAR"] == seleccion_instructor]
    
    if seleccion_motivo != "TODOS":
        data_filtrada = data_filtrada[data_filtrada["MOTIVO DE REEMPLAZO"] == seleccion_motivo]

    # Mostrar los datos filtrados
    st.subheader("Resultados Filtrados")
    st.dataframe(data_filtrada)

    # Mostrar resumen del número de reemplazos
    st.subheader("Resumen de Reemplazos")
    resumen = data_filtrada["INSTRUCTOR TITULAR"].value_counts().reset_index()
    resumen.columns = ["Instructor Titular", "Número de Reemplazos"]
    st.dataframe(resumen)

    # Agregar funcionalidad: Relacionar con clases totales y calcular % cumplimiento
    if not data_clases_totales.empty:
        # Contar reemplazos realizados por cada instructor titular
        reemplazos_contados = data_reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")

        # Cruzar los datos con el archivo de clases totales
        data_combinada = pd.merge(data_clases_totales, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")

        # Rellenar NaN en "REEMPLAZOS REALIZADOS" con 0 para instructores sin reemplazos
        data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)

        # Calcular el porcentaje de cumplimiento
        data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada["CLASES TOTALES 2024"]) * 100

        # Mostrar la tabla combinada con el % de cumplimiento
        st.subheader("Cumplimiento Anual por Instructor")
        st.dataframe(data_combinada)

        # Agregar opción para descargar los resultados
        @st.cache_data
        def convertir_a_excel(df):
            return df.to_excel(index=False, engine="openpyxl")

        st.download_button(
            label="Descargar Resultados en Excel",
            data=convertir_a_excel(data_combinada),
            file_name="cumplimiento_anual_instructores.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.warning("No se pudo cargar el archivo de reemplazos. Por favor, verifica la URL o el archivo Excel.")
