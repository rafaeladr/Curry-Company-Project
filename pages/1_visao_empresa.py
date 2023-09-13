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
#from PIL import Image
from datetime import datetime

st.set_page_config(page_title='Visão Empresa', layout='wide')

#=================
#Funções
#=================

def order_metric(df1):
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    # gráfico
    fig = px.bar( df_aux, x='Order_Date', y= 'ID')
    return fig

def traffic_order_share(df1):
    columns = ['ID', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    # gráfico
    fig = px.pie( df_aux, values='perc_ID', names='Road_traffic_density' )
    return fig

def traffic_order_city(df1):
    columns = ['ID', 'City', 'Road_traffic_density']
    df_aux = df1.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).count().reset_index()
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum())
    # gráfico
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    return fig

def order_by_week(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='ID' )
    return fig

def order_share_week(df1):
    df_aux1 = df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index()
    df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
    return fig

def country_maps(df1):
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
    # Desenhar o mapa
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup = location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width = 1024, height = 600)

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

st.header('Marketplace - Visão Cliente')

st.sidebar.markdown('# Cury Company') 
st.sidebar.markdown('## Fastest Delivery in the Town')
st.sidebar.markdown("""___""") 
st.sidebar.markdown('## Selecione uma Data Limite')
date_slider = st.sidebar.slider(
   'Até qual valor?',
    value=  datetime(2022, 4, 13),
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
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
    #Order Metric
        st.header('Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        col1, col2 = st.columns(2)
       
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width = True)
           
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df1)
            st.plotly_chart(fig, use_container_width = True)
    
with tab2:  
    with st.container():
        st.header('Order by Week')
        fig = order_by_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
    with st.container():
        st.header('Order Share by Week')
        fig = order_share_week(df1)
        st.plotly_chart(fig, use_container_width = True)
        
with tab3:
        st.header('Country Maps')
        country_maps(df1)

    


















