import streamlit as st
import pandas as pd

# Título de la aplicación
st.title("CRT v3: Class Recovery Tracker")

# Subtítulo
st.write("Visualización del consolidado de reemplazos de clases.")

# URL del archivo Excel en GitHub (raw)
url_excel = "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx"

try:
    # Leer el archivo Excel directamente desde la URL
    data = pd.read_excel(url_excel, engine="openpyxl")

    # Mostrar nombres reales de las columnas
    st.subheader("Nombres de las columnas en el archivo Excel:")
    st.write(data.columns.tolist())

    # Mensaje temporal para evitar más errores
    st.warning("Revisa el nombre exacto de la columna 'Instructor Titular' y actualízalo en el código.")

except Exception as e:
    st.error(f"Ocurrió un error al cargar el archivo: {e}")
