import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Configuración de la página
st.set_page_config(layout="wide")

# Título de la aplicación
st.markdown(
    "<h1 style='text-align: center;'>Sistema de Seguimiento y Cumplimiento de Instructores (CRT)</h1>",
    unsafe_allow_html=True,
)

# Selector de año
st.sidebar.title("Seleccione el Año de Análisis")
anio_seleccionado = st.sidebar.selectbox("Año:", ["Por favor seleccione un año", "2024", "2025"])

# Validación del año seleccionado
if anio_seleccionado == "Por favor seleccione un año":
    st.warning("Por favor seleccione un año para continuar.")
else:
    # URLs de los archivos Excel en GitHub según el año
    urls = {
        "2024": {
            "reemplazos": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx",
            "clases": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202024%20V2.xlsx",
        },
        "2025": {
            "reemplazos": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202025%20V1.xlsx",
            "clases": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202025%20V1.xlsx",
        },
    }

    # Función para cargar datos
    @st.cache_data
    def cargar_datos(url):
        return pd.read_excel(url, engine="openpyxl")

    # Cargar datos según el año seleccionado
    data_reemplazos = cargar_datos(urls[anio_seleccionado]["reemplazos"])
    data_clases_totales = cargar_datos(urls[anio_seleccionado]["clases"])

    # Proceso de análisis de datos
    if not data_reemplazos.empty and not data_clases_totales.empty:
        # Filtrado y cálculo de datos
        reemplazos_contados = data_reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")
        data_combinada = pd.merge(data_clases_totales, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")
        data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)
        data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada["CLASES TOTALES 2024"]) * 100

        # Filtros de búsqueda
        st.sidebar.subheader("Filtros de Búsqueda")
        nombres_instructores = sorted(data_combinada["NOMBRE INSTRUCTOR"].dropna().unique().tolist())
        termino_busqueda = st.sidebar.text_input("Escribe el nombre del instructor:")
        coincidencias = [nombre for nombre in nombres_instructores if termino_busqueda.lower() in nombre.lower()]
        seleccion_nombre = st.sidebar.selectbox("Selecciona un instructor:", ["Seleccione un instructor"] + coincidencias)

        if seleccion_nombre != "Seleccione un instructor":
            usuario_seleccionado = data_combinada[data_combinada["NOMBRE INSTRUCTOR"] == seleccion_nombre]["USUARIO INSTRUCTOR TITULAR"].iloc[0]
            datos_instructor = data_combinada[data_combinada["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]
            st.write(f"Cumplimiento Anual del Instructor: {seleccion_nombre}")
            st.dataframe(datos_instructor[["USUARIO INSTRUCTOR TITULAR", "CLASES TOTALES 2024", "REEMPLAZOS REALIZADOS", "% CUMPLIMIENTO"]])

        # Gráficos
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
            total_anual = reemplazos_por_mes['CANTIDAD'].sum()
            reemplazos_por_mes['PORCENTAJE'] = (reemplazos_por_mes['CANTIDAD'] / total_anual) * 100
            fig = px.bar(
                reemplazos_por_mes,
                x="MES",
                y="CANTIDAD",
                text="CANTIDAD",
                color="MES",
                title="Reemplazos Atendidos por Mes"
            )
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Programa":
            reemplazos_por_programa = data_reemplazos.groupby("PROGRAMA").size().reset_index(name="CANTIDAD")
            colores = {"UPC": "red", "UPN": "yellow", "CIBERTEC": "blue", "UPC EXTERNOS": "orange"}
            fig = px.bar(
                reemplazos_por_programa,
                x="PROGRAMA",
                y="CANTIDAD",
                color="PROGRAMA",
                color_discrete_map=colores,
                title="Reemplazos por Programa"
            )
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Motivo":
            reemplazos_por_motivo = data_reemplazos.groupby("MOTIVO DE REEMPLAZO").size().reset_index(name="CANTIDAD")
            fig = px.bar(
                reemplazos_por_motivo,
                x="MOTIVO DE REEMPLAZO",
                y="CANTIDAD",
                text="CANTIDAD",
                title="Reemplazos por Motivo"
            )
            fig.update_traces(marker_color=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
