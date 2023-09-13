import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home")

#image_path = 
#image = Image.open(image_path + 'logo.png')
#st.sidebar.image(width=120)

st.sidebar.markdown('# Cury Company') 
st.sidebar.markdown('## Fastest Delivery in the Town')
st.sidebar.markdown("""___""") 

st.write("# Cury Company Growth Dashboard")
st.markdown(
"""
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como usar este Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento;
        - Visão Tática: Indicadores semanais de crescimento;
        - Visao Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.

""")