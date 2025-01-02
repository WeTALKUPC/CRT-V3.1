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
    },
}

# Selector de año
st.subheader("Seleccione el Año de Análisis")
anio = st.selectbox("Año:", ["Por favor seleccione un año", "2024", "2025"])

if anio != "Por favor seleccione un año":
    # Cargar datos
    @st.cache_data
    def cargar_datos(url):
        try:
            return pd.read_excel(url, engine="openpyxl")
        except Exception as e:
            st.error(f"Error al cargar datos: {e}")
            return pd.DataFrame()

    data_reemplazos = cargar_datos(urls[anio]["reemplazos"])
    data_clases = cargar_datos(urls[anio]["clases"])

    # Verificar si los datos se cargaron correctamente
    if not data_reemplazos.empty and not data_clases.empty:
        reemplazos_contados = data_reemplazos.groupby("USUARIO INSTRUCTOR TITULAR").size().reset_index(name="REEMPLAZOS REALIZADOS")
        data_combinada = pd.merge(data_clases, reemplazos_contados, on="USUARIO INSTRUCTOR TITULAR", how="left")
        data_combinada["REEMPLAZOS REALIZADOS"] = data_combinada["REEMPLAZOS REALIZADOS"].fillna(0)
        data_combinada["% CUMPLIMIENTO"] = 100 - (data_combinada["REEMPLAZOS REALIZADOS"] / data_combinada["CLASES TOTALES 2024"]) * 100

        # Crear un diccionario para relacionar nombres y usuarios
        usuarios_a_nombres = dict(zip(data_combinada["USUARIO INSTRUCTOR TITULAR"], data_combinada["NOMBRE INSTRUCTOR"]))

        # Filtros de búsqueda
        st.subheader("Filtros de Búsqueda")
        nombres_instructores = sorted(data_combinada["NOMBRE INSTRUCTOR"].dropna().unique().tolist())
        termino_busqueda = st.text_input("Escribe el nombre del instructor:")
        coincidencias = [nombre for nombre in nombres_instructores if termino_busqueda.lower() in nombre.lower()]
        seleccion_nombre = st.selectbox("Selecciona un instructor de la lista:", ["Seleccione un instructor"] + coincidencias)

        if seleccion_nombre != "Seleccione un instructor":
            usuario_seleccionado = {v: k for k, v in usuarios_a_nombres.items()}.get(seleccion_nombre)
            datos_instructor = data_combinada[data_combinada["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]
            datos_instructor = datos_instructor.rename(columns={
                "USUARIO INSTRUCTOR TITULAR": "USUARIO INSTRUCTOR",
                "CLASES TOTALES 2024": "CLASES 2024",
                "REEMPLAZOS REALIZADOS": "REEMPLAZOS SOLICITADOS"
            })

            st.markdown(f"<h2 style='text-align: center;'>Cumplimiento Anual del Instructor: {seleccion_nombre}</h2>", unsafe_allow_html=True)
            col1, col2 = st.columns([3, 2])
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

            st.subheader("Detalle de Reemplazos Solicitados")
            detalle_reemplazos = data_reemplazos[data_reemplazos["USUARIO INSTRUCTOR TITULAR"] == usuario_seleccionado]
            detalle_reemplazos["FECHA DE CLASE"] = detalle_reemplazos["FECHA DE CLASE"].dt.date
            detalle_reemplazos = detalle_reemplazos.rename(columns={
                "USUARIO INSTRUCTOR REEMPLAZANTE": "USUARIO"
            }).drop(columns=["USUARIO INSTRUCTOR TITULAR"], errors="ignore")
            st.dataframe(detalle_reemplazos, use_container_width=True)

        # Gráficos
        st.subheader(f"Gráficos {anio}")
        opciones_graficos = ["Seleccione un gráfico", "Reemplazos por Mes", "Reemplazos por Programa", "Reemplazos por Motivo"]
        grafico_seleccionado = st.selectbox("Selecciona un gráfico:", opciones_graficos)

        if grafico_seleccionado == "Reemplazos por Mes":
            data_reemplazos["MES"] = data_reemplazos["FECHA DE CLASE"].dt.month
            reemplazos_por_mes = data_reemplazos.groupby("MES").size().reset_index(name="CANTIDAD")
            reemplazos_por_mes["MES"] = reemplazos_por_mes["MES"].replace({
                1: "ENERO", 2: "FEBRERO", 3: "MARZO", 4: "ABRIL", 5: "MAYO",
                6: "JUNIO", 7: "JULIO", 8: "AGOSTO", 9: "SEPTIEMBRE",
                10: "OCTUBRE", 11: "NOVIEMBRE", 12: "DICIEMBRE"
            })
            total_anual = reemplazos_por_mes["CANTIDAD"].sum()
            reemplazos_por_mes["PORCENTAJE"] = (reemplazos_por_mes["CANTIDAD"] / total_anual) * 100

            fig = go.Figure(data=[
                go.Bar(
                    x=reemplazos_por_mes["MES"],
                    y=reemplazos_por_mes["CANTIDAD"],
                    text=[f"{c}<br>{p:.1f}%" for c, p in zip(reemplazos_por_mes["CANTIDAD"], reemplazos_por_mes["PORCENTAJE"])],
                    textposition="outside",
                    marker=dict(color=px.colors.qualitative.Vivid)
                )
            ])
            fig.update_layout(title="Reemplazos Atendidos por Mes", xaxis_title="Mes", yaxis_title="Cantidad de Reemplazos", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Programa":
            reemplazos_por_programa = data_reemplazos.groupby("PROGRAMA").size().reset_index(name="CANTIDAD")
            fig = px.bar(
                reemplazos_por_programa, x="PROGRAMA", y="CANTIDAD",
                color="PROGRAMA", color_discrete_map={"UPC": "red", "UPN": "yellow"},
                text="CANTIDAD", title="Reemplazos por Programa"
            )
            fig.update_traces(textposition="outside")
            st.plotly_chart(fig, use_container_width=True)

        elif grafico_seleccionado == "Reemplazos por Motivo":
            reemplazos_por_motivo = data_reemplazos.groupby("MOTIVO DE REEMPLAZO").size().reset_index(name="CANTIDAD")
            fig = px.bar(
                reemplazos_por_motivo, x="MOTIVO DE REEMPLAZO", y="CANTIDAD",
                color="MOTIVO DE REEMPLAZO", text="CANTIDAD", title="Reemplazos por Motivo"
            )
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No se pudieron cargar los datos. Por favor, verifica los archivos.")
