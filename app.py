import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("Dashboard de Cumplimiento Anual por Instructor")

# URLs de los archivos Excel en GitHub
url_reemplazos = "https://github.com/WeTALKUPC/CRT-V3.1/blob/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx?raw=true"
url_clases_totales = "https://github.com/WeTALKUPC/CRT-V3.1/blob/main/CONSOLIDADO%20CLASES%202024%20V2.xlsx?raw=true"

# Función para cargar los datos
@st.cache_data
def cargar_datos():
    reemplazos = pd.read_excel(url_reemplazos)
    clases_totales = pd.read_excel(url_clases_totales)
    return reemplazos, clases_totales

# Cargar los datos
reemplazos, clases_totales = cargar_datos()

# Procesar los datos
# Contar los reemplazos realizados por cada instructor titular
reemplazos_contados = reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")

# Cruzar los datos con el archivo de clases totales
data_combinada = pd.merge(clases_totales, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")

# Rellenar NaN en "REEMPLAZOS REALIZADOS" con 0 para instructores sin reemplazos
data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)

# Calcular el porcentaje de cumplimiento
data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada["CLASES TOTALES 2024"]) * 100

# Mostrar la tabla combinada
st.subheader("Cumplimiento Anual por Instructor")
st.dataframe(data_combinada)

# Descargar los resultados como un archivo Excel
@st.cache_data
def convertir_a_excel(df):
    return df.to_excel(index=False, engine="openpyxl")

st.download_button(
    label="Descargar Resultados en Excel",
    data=convertir_a_excel(data_combinada),
    file_name="cumplimiento_anual_instructores.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
