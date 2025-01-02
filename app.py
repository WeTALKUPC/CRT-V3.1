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

    # Opciones de búsqueda
    nombres_instructores = sorted(data_combinada["NOMBRE INSTRUCTOR"].dropna().unique().tolist())

    # Barra de búsqueda por nombre
    st.write("Busca un instructor por nombre:")
    termino_busqueda = st.text_input("Escribe el nombre del instructor:")
    coincidencias = [nombre for nombre in nombres_instructores if termino_busqueda.lower() in nombre.lower()]

    # Selector para nombres coincidentes
    seleccion_nombre = st.selectbox(
        "Selecciona un instructor de la lista:",
        ["Seleccione un instructor"] + coincidencias,
    )

    # Obtener el usuario del instructor seleccionado
    if seleccion_nombre != "Seleccione un instructor":
        usuario_seleccionado = {v: k for k, v in usuarios_a_nombres.items()}.get(seleccion_nombre)

        # Filtrar los datos para el instructor seleccionado
        datos_instructor = data_combinada[data_combinada["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]

        # Renombrar columnas para el cuadro de cumplimiento anual
        datos_instructor = datos_instructor.rename(columns={
            "USUARIO INSTRUCTOR TITULAR": "USUARIO INSTRUCTOR",
            "CLASES TOTALES 2024": "CLASES 2024",
            "REEMPLAZOS REALIZADOS": "REEMPLAZOS SOLICITADOS"
        })

        # Mostrar el texto de cumplimiento anual en grande y centrado
        st.markdown(
            f"<h2 style='text-align: center; width: 100%;'>{f'Cumplimiento Anual del Instructor: {seleccion_nombre}'}</h2>",
            unsafe_allow_html=True,
        )

        # Mostrar el cumplimiento anual y el gráfico circular en la misma fila con más espacio
        col1, col2 = st.columns([3, 2])  # Ajustar proporciones de las columnas

        with col1:
            st.dataframe(datos_instructor[["USUARIO INSTRUCTOR", "CLASES 2024", "REEMPLAZOS SOLICITADOS", "% CUMPLIMIENTO"]])

        with col2:
            reemplazos = datos_instructor["REEMPLAZOS SOLICITADOS"].iloc[0]
            cumplimiento = datos_instructor["CLASES 2024"].iloc[0] - reemplazos
            fig = px.pie(
                names=["Clases Cumplidas", "Reemplazos Solicitados"],
                values=[cumplimiento, reemplazos],
            )
            st.plotly_chart(fig, use_container_width=True)

        # Mostrar detalle de reemplazos solicitados debajo
        st.subheader("Detalle de Reemplazos Solicitados")
        detalle_reemplazos = data_reemplazos[data_reemplazos["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]

        # Modificar la columna de fecha para eliminar el tiempo
        detalle_reemplazos["FECHA DE CLASE"] = detalle_reemplazos["FECHA DE CLASE"].dt.date

        # Renombrar columna "USUARIO INSTRUCTOR REEMPLAZANTE" a "USUARIO"
        detalle_reemplazos = detalle_reemplazos.rename(columns={
            "USUARIO INSTRUCTOR REEMPLAZANTE": "USUARIO"
        })

        # Eliminar columnas no deseadas
        detalle_reemplazos = detalle_reemplazos.drop(columns=[
            "HORA INICIO DE CLASE", "HORA FIN DE CLASE", "INSTRUCTOR TITULAR", "USUARIO INSTRUCTOR TITULAR"
        ], errors="ignore")

        st.dataframe(detalle_reemplazos, use_container_width=True)

else:
    st.warning("No se pudieron cargar los datos. Por favor, verifica los archivos.")
