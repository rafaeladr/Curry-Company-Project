#libraries
import pandas as pd
import numpy as np
import io
import re
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
import streamlit as st
from datetime import datetime
#from PIL import image

st.set_page_config(page_title='Visão Restaurantes', layot='wide')

#=================
#Funções
#=================

        
def distance(df1):
    cols = ['Restaurant_latitude', 'Restaurant_longitude',	'Delivery_location_latitude',	'Delivery_location_longitude']
    df1['distance']= (df1.loc[:, cols].apply(lambda x : haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                      (x['Delivery_location_latitude'], 
                                                                       x['Delivery_location_longitude'])), axis= 1))
    avg_distance = np.round( df1['distance'].mean(), 3)
    return avg_distance

def avg_std_time_deliver(df1, festival, op):
    df1_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    linhas_selecionadas = df1_aux['Festival'] == festival
    df1_aux = np.round(df1_aux.loc[linhas_selecionadas, op], 2)
    return df1_aux


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

st.header('Marketplace - Visão Restaurantes')

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
with st.container():
    st.title("Overall Metrics")
    st.markdown("""---""")
    col1, col2, col3, col4, col5, col6 = st.columns (6)
    with col1:
        del_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
        col1.metric('Entregadores Únicos', del_unique)
        
    with col2:
        avg_distance = distance(df1)
        col2.metric('Distância Média de Entregas', avg_distance)

    with col3:
        df1_aux = avg_std_time_deliver(df1, 'Yes', 'avg_time')
        col3.metric('Tempo Médio de Entrega em Festivais', df1_aux)
        
    with col4:
        df1_aux = avg_std_time_deliver(df1, 'Yes', 'std_time')
        col4.metric('Desvio Padrão Médio de Entrega em Festivais', df1_aux)
        
    with col5:
        df1_aux = avg_std_time_deliver(df1, 'No', 'avg_time')
        col5.metric('Tempo Médio de Entrega sem Festivais', df1_aux)
        
    with col6:
        df1_aux = avg_std_time_deliver(df1, 'No', 'std_time')       
        col6.metric('Desvio Padrão Médio de Entrega sem Festivais', df1_aux)
        
with st.container(): 
        st.markdown("""---""")
        st.title("Tempo Médio de Entrega por Cidade")
        df1_aux = df1.loc[:, ['Time_taken(min)', 'City']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
        df1_aux.columns = ['avg_time', 'std_time']
        df1_aux = df1_aux.reset_index()
        fig = go.Figure()
        fig.add_trace((go.Bar(name='Control', x=df1_aux['City'], y=df1_aux['avg_time'], error_y= dict(type= 'data', array =
                                                                                                      df1_aux['std_time']))))
        fig.update_layout(barmode = 'group')
        st.plotly_chart(fig)

with st.container():
    st.markdown("""---""")
    st.title("Distribuição do Tempo")
    col1, col2= st.columns (2)
    with col1:
        cols = ['Restaurant_latitude', 'Restaurant_longitude',	'Delivery_location_latitude',	'Delivery_location_longitude']
        df1['distance']= df1.loc[:, cols].apply(lambda x : haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                          (x['Delivery_location_latitude'],	x['Delivery_location_longitude'])), axis= 1)
        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data = [go.Pie(labels= avg_distance['City'] , values = avg_distance['distance'], pull=[0, 0.1, 0])])
        st.plotly_chart(fig)
        
       
    with col2:
        cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
        df1_aux = df1.loc[:, cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
        df1_aux.columns = ['avg_time', 'std_time']
        df1_aux = df1_aux.reset_index()

        fig = px.sunburst(df1_aux, path=['City','Road_traffic_density'], values= 'avg_time', color= 'std_time', 
                          color_continuous_scale = 'RdBu', color_continuous_midpoint= np.average(df1_aux['std_time']))
        st.plotly_chart(fig)

with st.container():
    st.markdown("""---""")
    st.title("Distribuição da Distância")
    df1_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
    df1_aux.columns = ['avg_time', 'std_time']
    df1_aux = df1_aux.reset_index()
    st.dataframe(df1_aux)


