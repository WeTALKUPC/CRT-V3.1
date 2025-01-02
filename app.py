import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configurar el diseño en ancho completo
st.set_page_config(layout="wide")

# Título centrado de la aplicación
st.markdown(
    "<h1 style='text-align: center;'>Sistema de Seguimiento y Cumplimiento de Instructores (CRT)</h1>",
    unsafe_allow_html=True,
)

# URLs de los archivos Excel en GitHub (raw)
urls = {
    "2024": {
        "reemplazos": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx",
        "clases": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202024%20V2.xlsx",
    },
    "2025": {
        "reemplazos": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202025%20V1.xlsx",
        "clases": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202025%20V1.xlsx",
    }
}

# Función para cargar datos desde un archivo Excel
@st.cache_data
def cargar_datos(url):
    try:
        data = pd.read_excel(url, engine="openpyxl")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo: {e}")
        return pd.DataFrame()

# Mostrar el selector de año
st.subheader("Seleccione el Año de Análisis")
anio_seleccionado = st.selectbox("Año:", ["Seleccione un año"] + list(urls.keys()))

# Mostrar contenido solo si se selecciona un año válido
if anio_seleccionado != "Seleccione un año":
    # Cargar los datos correspondientes al año seleccionado
    data_reemplazos = cargar_datos(urls[anio_seleccionado]["reemplazos"])
    data_clases_totales = cargar_datos(urls[anio_seleccionado]["clases"])

    if not data_reemplazos.empty and not data_clases_totales.empty:
        # Contar reemplazos realizados por cada instructor titular
        reemplazos_contados = data_reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")

        # Cruzar los datos con el archivo de clases totales
        data_combinada = pd.merge(data_clases_totales, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")

        # Rellenar NaN en "REEMPLAZOS REALIZADOS" con 0 para instructores sin reemplazos
        data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)

        # Calcular el porcentaje de cumplimiento
        data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada["CLASES TOTALES 2024"]) * 100

        # Mostrar filtros
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

        # Mostrar gráficos y filtros si se selecciona un instructor
        if seleccion_nombre != "Seleccione un instructor":
            usuario_seleccionado = dict(zip(data_combinada["NOMBRE INSTRUCTOR"], data_combinada["USUARIO INSTRUCTOR TITULAR"])).get(seleccion_nombre)

            datos_instructor = data_combinada[data_combinada["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]

            st.markdown(
                f"<h2 style='text-align: center;'>Cumplimiento Anual del Instructor: {seleccion_nombre}</h2>",
                unsafe_allow_html=True,
            )

            col1, col2 = st.columns([3, 2])

            with col1:
                st.dataframe(datos_instructor[["USUARIO INSTRUCTOR TITULAR", "CLASES TOTALES 2024", "REEMPLAZOS REALIZADOS", "% CUMPLIMIENTO"]])

            with col2:
                fig = px.pie(
                    names=["Clases Cumplidas", "Reemplazos Solicitados"],
                    values=[datos_instructor["CLASES TOTALES 2024"].iloc[0] - datos_instructor["REEMPLAZOS REALIZADOS"].iloc[0],
                            datos_instructor["REEMPLAZOS REALIZADOS"].iloc[0]],
                )
                st.plotly_chart(fig, use_container_width=True)

            # Mostrar detalle de reemplazos
            st.subheader("Detalle de Reemplazos Solicitados")
            detalle_reemplazos = data_reemplazos[data_reemplazos["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]
            detalle_reemplazos = detalle_reemplazos.drop(columns=[
                "HORA INICIO DE CLASE", "HORA FIN DE CLASE", "INSTRUCTOR TITULAR"
            ], errors="ignore")
            st.dataframe(detalle_reemplazos)

        # Gráficos generales
        st.subheader(f"Gráficos {anio_seleccionado}")
        opciones_graficos = ["Seleccione un gráfico", "Reemplazos por Mes", "Reemplazos por Programa", "Reemplazos por Motivo"]
        grafico_seleccionado = st.selectbox("Selecciona un gráfico:", opciones_graficos)

        if grafico_seleccionado == "Reemplazos por Mes":
            data_reemplazos['MES'] = data_reemplazos['FECHA DE CLASE'].dt.month
            reemplazos_por_mes = data_reemplazos.groupby('MES').size().reset_index(name='CANTIDAD')
            reemplazos_por_mes['MES'] = reemplazos_por_mes['MES'].replace({
                1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
                7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
            })
            fig = px.bar(reemplazos_por_mes, x='MES', y='CANTIDAD', text='CANTIDAD', title="Reemplazos por Mes")
            fig.update_traces(textposition="auto")
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Programa":
            reemplazos_por_programa = data_reemplazos.groupby("PROGRAMA").size().reset_index(name="CANTIDAD")
            fig = px.bar(reemplazos_por_programa, x='PROGRAMA', y='CANTIDAD', text='CANTIDAD', title="Reemplazos por Programa")
            fig.update_traces(textposition="auto")
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Motivo":
            reemplazos_por_motivo = data_reemplazos.groupby("MOTIVO DE REEMPLAZO").size().reset_index(name="CANTIDAD")
            fig = px.bar(reemplazos_por_motivo, x='MOTIVO DE REEMPLAZO', y='CANTIDAD', text='CANTIDAD', title="Reemplazos por Motivo")
            fig.update_traces(textposition="auto")
            st.plotly_chart(fig, use_container_width=True)
