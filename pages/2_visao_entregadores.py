#libraries
import pandas as pd
import numpy as np
import io
import re
from haversine import haversine
import plotly.express as px
import plotly.graph_objects
import folium
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
#from PIL import Image

st.set_page_config(page_title='Visão Entregadores', layout='wide')

#=================
#Funções
#=================
def top_fastest_delivers(df1):
    df2 = (df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['Time_taken(min)', 'City'], ascending = True).reset_index())
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat( [df_aux01,df_aux02, df_aux03]).reset_index(drop = True)
    return df3

def top_slowest_deliveries(df1):
    df2 = (df1.loc[:, ['Time_taken(min)', 'City', 'Delivery_person_ID']].groupby(['City', 'Delivery_person_ID']).mean().sort_values(['Time_taken(min)', 'City'], ascending = False).reset_index())
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat( [df_aux01,df_aux02, df_aux03]).reset_index(drop = True)
    return df3

def clean_code(df1):
    """
    Função de responsabilidade de Limpeza do Dataframe
    Tipos de Limpeza:
        1. Remoção de dados NaN
        2. Conversão de tipos de colunas
        3. Remoção de espaços nas variáveis de texto
        4. Formatação de datas
        5. Limpeza da coluna de tempo
        
        INPUT: Dataframe
        OUTPUT: Dataframe
    """
# Limpeza da base
    linhas_selecionadas = (df1["Delivery_person_Age"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1["City"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1["City"] != "NaN")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1["Road_traffic_density"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1["Festival"] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Vehicle_condition'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['multiple_deliveries'] != "NaN ")
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1["Delivery_person_Age"] = df1["Delivery_person_Age"].astype(int)

    df1["Delivery_person_Ratings"] = df1["Delivery_person_Ratings"].astype(float)

    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(str)

    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    df1.loc[:,'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:,'multiple_deliveries'] = df1.loc[:, 'multiple_deliveries'].str.strip()

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.replace('(min) ', ''))
    linhas_selecionadas = (df1['Time_taken(min)'] != "nan")
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1["Time_taken(min)"] = df1["Time_taken(min)"].astype(int)

    return df1

#=================
#Import Dataset
#=================
df = pd.read_csv('train.csv')

#=================
#Limpeza da base
#=================
df1 = clean_code(df)

#========================
# Barra Lateral Streamlit
#========================

st.header('Marketplace - Visão Entregadores')

st.sidebar.markdown('# Cury Company') 
st.sidebar.markdown('## Fastest Delivery in the Town')
st.sidebar.markdown("""___""") 
st.sidebar.markdown('## Selecione uma Data Limite')
date_slider = st.sidebar.slider(
   'Até qual valor?',
    value= datetime(2022, 4, 13),
    min_value= datetime(2022, 2, 11),
    max_value= datetime(2022, 4, 6),
    format= 'DD-MM-YYYY')
st.header(date_slider)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?', ('Low', 'Medium', 'High', 'Jam'), default= ['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""") 

#Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#===================
# Layout Streamlit
#===================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '', ''])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns (4, gap = 'large')
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)
            
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição', melhor_condicao)
            
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição', pior_condicao)
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
            
        col1, col2 = st.columns (2)
        with col1:
            st.subheader('Avaliação média por entregador')
            df_avg_avaliacao_entregador = df1.loc[:, ['Delivery_person_Ratings',                                 'Delivery_person_ID']].groupby(['Delivery_person_Ratings','Delivery_person_ID']).mean().reset_index()                
            st.dataframe(df_avg_avaliacao_entregador)
                
        with col2:
            st.subheader('Avaliação média por trânsito')
            df_avg_avaliacao_transito = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby(['Road_traffic_density']).agg({'Delivery_person_Ratings' : ('mean', 'std')})
            df_avg_avaliacao_transito.columns = ['delivery_mean', 'delivery_std']
            df_avg_avaliacao_transito = df_avg_avaliacao_transito.reset_index()
            st.dataframe(df_avg_avaliacao_transito)
            
            st.subheader('Avaliação média por clima')
            df_avg_avaliacao_clima = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ('mean', 'std')})
            df_avg_avaliacao_clima.columns = ['delivery_mean', 'delivery_std']
            df_avg_avaliacao_clima = df_avg_avaliacao_clima.reset_index()
            st.dataframe(df_avg_avaliacao_clima)
                
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns (2)
        with col1:
            st.subheader('Top Entregadores mais rápidos')
            df3 = top_fastest_delivers(df1)
            st.dataframe(df3)

        with col2:
            st.subheader('Top Entregadores mais lentos')
            df3 = top_slowest_deliveries(df1)
            st.dataframe(df3)
           
            
