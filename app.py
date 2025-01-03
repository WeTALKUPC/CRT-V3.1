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
    2024: {
        "reemplazos": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202024%20V2.xlsx",
        "clases": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202024%20V2.xlsx",
    },
    2025: {
        "reemplazos": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20REEMPLAZOS%202025%20V1.xlsx",
        "clases": "https://raw.githubusercontent.com/WeTALKUPC/CRT-V3.1/main/CONSOLIDADO%20CLASES%202025%20V1.xlsx",
    },
}

# Selección del año
st.subheader("Seleccione el Año de Análisis")
anio_seleccionado = st.selectbox("Año:", ["Por favor seleccione un año", 2024, 2025])

# Verificar si se seleccionó un año válido
if anio_seleccionado != "Por favor seleccione un año":
    # Cargar datos según el año seleccionado
    @st.cache_data
    def cargar_datos_reemplazos(url):
        try:
            data = pd.read_excel(url, engine="openpyxl")
            return data
        except Exception as e:
            st.error(f"Error al cargar el archivo de reemplazos: {e}")
            return pd.DataFrame()

    @st.cache_data
    def cargar_datos_clases(url):
        try:
            data = pd.read_excel(url, engine="openpyxl")
            return data
        except Exception as e:
            st.error(f"Error al cargar el archivo de clases totales: {e}")
            return pd.DataFrame()

    # Cargar datos
    data_reemplazos = cargar_datos_reemplazos(urls[anio_seleccionado]["reemplazos"])
    data_clases_totales = cargar_datos_clases(urls[anio_seleccionado]["clases"])

    # Verificar si los datos se cargaron correctamente
    if not data_reemplazos.empty and not data_clases_totales.empty:
        # Procesar los datos (igual que antes)
        reemplazos_contados = data_reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")
        data_combinada = pd.merge(data_clases_totales, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")
        data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)
        data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada[f"CLASES TOTALES {anio_seleccionado}"]) * 100
        usuarios_a_nombres = dict(zip(data_combinada["USUARIO INSTRUCTOR TITULAR"], data_combinada["NOMBRE INSTRUCTOR"]))

        # Filtros de búsqueda
        st.subheader("Filtros de Búsqueda")
        nombres_instructores = sorted(data_combinada["NOMBRE INSTRUCTOR"].dropna().unique().tolist())
        st.write("Busca un instructor por nombre:")
        termino_busqueda = st.text_input("Escribe el nombre del instructor:")
        coincidencias = [nombre for nombre in nombres_instructores if termino_busqueda.lower() in nombre.lower()]
        seleccion_nombre = st.selectbox("Selecciona un instructor de la lista:", ["Seleccione un instructor"] + coincidencias)

        # Detalle del instructor seleccionado
        if seleccion_nombre != "Seleccione un instructor":
            usuario_seleccionado = {v: k for k, v in usuarios_a_nombres.items()}.get(seleccion_nombre)
            datos_instructor = data_combinada[data_combinada["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]
            datos_instructor = datos_instructor.rename(columns={
                "USUARIO INSTRUCTOR TITULAR": "USUARIO INSTRUCTOR",
                f"CLASES TOTALES {anio_seleccionado}": "CLASES",
                "REEMPLAZOS REALIZADOS": "REEMPLAZOS SOLICITADOS",
            })
            st.markdown(
                f"<h2 style='text-align: center;'>Cumplimiento Anual del Instructor: {seleccion_nombre}</h2>",
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns([3, 2])
            with col1:
                st.dataframe(datos_instructor[["USUARIO INSTRUCTOR", "CLASES", "REEMPLAZOS SOLICITADOS", "% CUMPLIMIENTO"]])
            with col2:
                reemplazos = datos_instructor["REEMPLAZOS SOLICITADOS"].iloc[0]
                cumplimiento = datos_instructor["CLASES"].iloc[0] - reemplazos
                fig = px.pie(names=["Clases Cumplidas", "Reemplazos Solicitados"], values=[cumplimiento, reemplazos])
                st.plotly_chart(fig, use_container_width=True)

            st.subheader("Detalle de Reemplazos Solicitados")
            detalle_reemplazos = data_reemplazos[data_reemplazos["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]
            detalle_reemplazos["FECHA DE CLASE"] = detalle_reemplazos["FECHA DE CLASE"].dt.date
            detalle_reemplazos = detalle_reemplazos.rename(columns={"USUARIO INSTRUCTOR REEMPLAZANTE": "USUARIO"})
            detalle_reemplazos = detalle_reemplazos.drop(columns=["HORA INICIO DE CLASE", "HORA FIN DE CLASE", "INSTRUCTOR TITULAR", "USUARIO INSTRUCTOR TITULAR"], errors="ignore")
            st.dataframe(detalle_reemplazos, use_container_width=True)

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
            colores_pastel = px.colors.qualitative.Pastel
            fig = go.Figure(data=[go.Bar(x=reemplazos_por_mes['MES'], y=reemplazos_por_mes['CANTIDAD'], text=[f"{c}<br>{p:.1f}%" for c, p in zip(reemplazos_por_mes['CANTIDAD'], reemplazos_por_mes['PORCENTAJE'])], textposition='auto', marker=dict(color=colores_pastel))])
            fig.update_layout(title=f"Reemplazos Atendidos por Mes en {anio_seleccionado}", xaxis_title="Mes", yaxis_title="Cantidad de Reemplazos", template="simple_white", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Programa":
            reemplazos_por_programa = data_reemplazos.groupby("PROGRAMA").size().reset_index(name="CANTIDAD")
            colores = {"UPC": "red", "UPN": "yellow", "CIBERTEC": "blue", "UPC EXTERNOS": "orange"}
            fig = px.bar(reemplazos_por_programa, x="PROGRAMA", y="CANTIDAD", color="PROGRAMA", title=f"Reemplazos por Programa en {anio_seleccionado}", text="CANTIDAD", color_discrete_map=colores)
            fig.update_traces(textposition='auto')
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Motivo":
            reemplazos_por_motivo = data_reemplazos.groupby("MOTIVO DE REEMPLAZO").size().reset_index(name="CANTIDAD")
            fig = px.bar(reemplazos_por_motivo, x="MOTIVO DE REEMPLAZO", y="CANTIDAD", title=f"Reemplazos por Motivo en {anio_seleccionado}", text="CANTIDAD", color="CANTIDAD", color_continuous_scale=px.colors.sequential.Sunset)
            fig.update_traces(textposition='auto')
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No se pudieron cargar los datos. Por favor, verifica los archivos.")
else:
    st.info("Seleccione un año para iniciar el análisis.")
