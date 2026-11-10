import streamlit as st
from src.interface.dashboard import render_simulation

st.set_page_config(
    page_title="EpiSim",
    page_icon="🧬",
    layout="wide"
)

st.title("EpiSim")

st.caption("Simulador computacional epidemiológico")

st.sidebar.title("Navegação")

page = st.sidebar.radio(
    "Menu principal",
    [
        "Visão geral",
        "Simulador",
        "Análise",
        "Doenças"
    ]
)

if page == "Visão geral":

    st.header("Visão geral")

    col1, col2, col3 = st.columns(3)

    col1.metric("Simulações", "0")
    col2.metric("Doenças", "0")
    col3.metric("População", "0")

    st.info("Ainda não existem simulações registradas.")

elif page == "Simulador":
    render_simulation()

elif page == "Análise":

    st.header("Análise epidemiológica")

    st.info("Os gráficos aparecerão aqui.")

elif page == "Doenças":

    st.header("Doenças cadastradas")

    st.write("Catálogo de doenças do EpiSim.")