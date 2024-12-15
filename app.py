import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Dashboard de Cumplimiento por Feriado, Programa e Instructor")

# URL del archivo Excel en GitHub (raw)
url_excel = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx"

# Cargar el archivo Excel
@st.cache_data
def cargar_datos():
    try:
        data = pd.read_excel(url_excel, engine="openpyxl")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# Cargar los datos
data = cargar_datos()

# Verificar si el archivo se cargó correctamente
if not data.empty:
    # Crear los filtros
    st.subheader("Filtros de Búsqueda")

    # Filtro de instructor titular
    instructores = ["TODOS"] + sorted(data["Instructor Titular"].dropna().unique().tolist())
    seleccion_instructor = st.selectbox("Selecciona un instructor titular:", instructores)

    # Filtro de motivo de reemplazo
    motivos = ["TODOS"] + sorted(data["Motivo del Reemplazo"].dropna().unique().tolist())
    seleccion_motivo = st.selectbox("Selecciona un motivo de reemplazo:", motivos)

    # Filtrar los datos según la selección
    data_filtrada = data.copy()
    
    if seleccion_instructor != "TODOS":
        data_filtrada = data_filtrada[data_filtrada["Instructor Titular"] == seleccion_instructor]
    
    if seleccion_motivo != "TODOS":
        data_filtrada = data_filtrada[data_filtrada["Motivo del Reemplazo"] == seleccion_motivo]

    # Mostrar los datos filtrados
    st.subheader("Resultados Filtrados")
    st.dataframe(data_filtrada)

    # Mostrar resumen del número de reemplazos
    st.subheader("Resumen de Reemplazos")
    resumen = data_filtrada["Instructor Titular"].value_counts().reset_index()
    resumen.columns = ["Instructor Titular", "Número de Reemplazos"]
    st.dataframe(resumen)

else:
    st.warning("No se pudo cargar el archivo. Por favor, verifica la URL o el archivo Excel.")

