#Importando pacotes 

import pandas as pd
import plotly as py
import plotly.express as px
from haversine import haversine
from PIL import Image
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerClusterfrom folium.plugins import MarkerCluster

#Crio uma página no stremlit onde será configurado as ações
#Chamo a página no terminal -> streamlit run 

st.set_page_config(page_title='City', page_icon=':)', layout = 'wide')

#Import dataset

dataframe = pd.read_csv('dataset/zomato.csv')
df = dataframe.copy()
print(df)


#=========================================================#
##          FUNÇÕES DA LIMPEZA DOS  DADOS                 #
#=========================================================#

#Preenchimento do nome dos Países

COUNTRIES = {
    1: 'India',
    14:'Australia',
    30:'Brazil',
    37:'Canada',
    94:'Indonesia',
    148:'New Zeland',
    162:'Philippines',
    166:'Quatar',
    184:'Singapure',
    189:'South Africa',
    191:'Sri Lanka',
    208:'Turkey',
    214:'United Arab Emirates',
    215:'England',
    216:'United States of America',
}
def country_names(country_id):
    return COUNTRIES[country_id]

#Criação do Tipo de Categoria de Comida

def create_price_type(price_range):
    if price_range == 1:
       return 'cheap'
    elif price_range ==2:
       return 'normal'
    elif price_range == 3:
        return 'expensive'
    else:
        return 'gourmet'

#Criação do nome das Cores

COLORS = {
    '3F7E00': 'darkgreen',
    '5BA829': 'green',
    '9ACD32': 'lightgreen',
    'CDD614': 'orange',
    'FFBA00': 'red',
    'CBCBC8': 'darkred',
    'FF7800': 'darkred',
}

def color_name(color_code):
    return COLORS[color_code]

#=========================================================#
##           LIMPEZA DOS  DADOS                           #
#=========================================================#
## Troca os códigos do Country Code por nomes

for index, row in df.iterrows():  
    df.loc[index, 'Country Code'] = country_names(row['Country Code'])

# Substituição do numero de range price por string de goumert/expensive

for index, row in df.iterrows():  
    df.loc[index, 'Price range'] = create_price_type(row['Price range'])

#Substituição codigo por cores

for index, row in df.iterrows():  
    df.loc[index, 'Rating color'] = color_name(row['Rating color'])


#Remoção dos NaN do Cuisines
df= df.dropna(inplace = False, axis = 0)

# Categorização dos restaurantes por um tipo de culinária

df["Cuisines"] = df.loc[:, "Cuisines"].apply(lambda x: str(x).split(",")[0])

##RENOMEANDO NOME DA COLUNA COUNTRY

df.rename(index =str, columns = {'Country Code':'Country'}, inplace = True)

#Remoção da coluna usando a função drop/ Esta coluna possui apenas o valor 0 em todas as linhas
df = df.drop("Switch to order menu", axis=1)

#Verificação de dados duplicados dentro do dataframe
duplicados = df.duplicated()
duplicados.sum()

# Exclusão dos dados duplicados no DF. Inplace= false retorna o mesmo dataframe sem as duplicatas
df = df.drop_duplicates(keep = 'first', inplace = False)

#===========================================================================================#
#     LAYOUT DO STREMEALIT - BARRA LATERAL                                                  #
#===========================================================================================#

st.header('Zomato Restaurants  - A melhor opção em todo mundo')

image_path = 'zomato.png'
image=Image.open('zomato.png')
st.sidebar.image( image,width=210)

st.sidebar.markdown('# City')
st.sidebar.markdown("""___""")

st.sidebar.markdown("""___""")

#Criar filtros de País
pais_options = st.sidebar.multiselect(
  'Selecione o País de interesse:',
  ['Philippines', 'Brazil', 'Australia', 'United States of America',
       'Canada', 'Singapure', 'United Arab Emirates', 'India',
       'Indonesia', 'New Zeland', 'England', 'Quatar', 'South Africa',
       'Sri Lanka', 'Turkey'],
  default= ['United States of America',
      'Brazil', 'United Arab Emirates', 'India'])

cidades_options = st.sidebar.multiselect(
  'Selecione a cidade de interesse:',
  ['Las Piñas City', 'Makati City', 'Mandaluyong City', 'Manila',
       'Marikina City', 'Muntinlupa City', 'Pasay City', 'Pasig City',
       'Quezon City', 'San Juan City', 'Tagaytay City', 'Taguig City',
       'Brasília', 'Rio de Janeiro', 'São Paulo', 'Adelaide', 'Atlanta',
       'Austin', 'Boston', 'Brisbane', 'Calgary', 'Charlotte', 'Chicago',
       'Dallas', 'Denver', 'Detroit', 'Houston', 'Las Vegas',
       'Los Angeles', 'Miami', 'Montreal', 'New Orleans', 'New York City',
       'Ottawa', 'Perth', 'Philadelphia', 'Phoenix', 'Portland',
       'San Antonio', 'San Diego', 'San Francisco', 'Seattle',
       'Singapore', 'Washington DC', 'Abu Dhabi', 'Dubai', 'Fujairah',
       'Sharjah', 'Agra', 'Ahmedabad', 'Allahabad', 'Amritsar',
       'Aurangabad', 'Bangalore', 'Bhopal', 'Bhubaneshwar', 'Chandigarh',
       'Chennai', 'Coimbatore', 'Dehradun', 'Gandhinagar', 'Gangtok',
       'Ghaziabad', 'Goa', 'Gurgaon', 'Guwahati', 'Hyderabad', 'Indore',
       'Jaipur', 'Kanpur', 'Kochi', 'Kolkata', 'Lucknow', 'Ludhiana',
       'Mangalore', 'Mohali', 'Mumbai', 'Mysore', 'Nagpur', 'Nashik',
       'Nasik', 'New Delhi', 'Noida', 'Ooty', 'Panchkula', 'Patna',
       'Puducherry', 'Pune', 'Ranchi', 'Secunderabad', 'Shimla', 'Surat',
       'Thane', 'Vadodara', 'Varanasi', 'Vizag', 'Zirakpur', 'Bogor',
       'Jakarta', 'Tangerang', 'Auckland', 'Hamilton', 'Wellington',
       'Wellington City', 'Birmingham', 'Edinburgh', 'Glasgow', 'London',
       'Manchester', 'Doha', 'Cape Town', 'Clarens', 'Durban',
       'East Rand', 'Inner City', 'Johannesburg', 'Johannesburg South',
       'Midrand', 'Pretoria', 'Randburg', 'Roodepoort', 'Sandton',
       'Colombo', 'Ankara', 'İstanbul'],
  default= ['Rio de Janeiro', 'São Paulo', 'Adelaide', 'Birmingham'])

st.sidebar.markdown('#### Powered by Umpozzobom')
st.sidebar.markdown("""___""")

#===========================================================================================#
#     LAYOUT DO STREMEALIT - criação das tabs com as informações a serem apresentadas       #
#===========================================================================================#
tab1,tab2= st.tabs (['City','--'])  

with tab1:
     with st.container():
        col1,col2 = st.columns(2)
        with col1:
           st.markdown('** Top 10 Restaurantes registrados por Cidade**')
           df_aux = df.loc[ :, [ 'City', 'Restaurant ID']].groupby(['City']).count().sort_values(by = 'Restaurant ID', ascending = False).head(5)
           st.dataframe(df_aux)
        with col2:
           st.write('**Top 10 cidades cujos restaurantes realizam reserva de mesa, pedidos online e delivery**') 
           df_aux = (df.loc[:, ['Country', 'City', 'Has Table booking','Has Online delivery','Is delivering now']].groupby(['Country', 'City'])
            .sum().sort_values(by = ['Has Table booking', 'Has Online delivery','Is delivering now'], ascending= [False,True,True])).head(10).reset_index()
           st.table(df_aux)

     with st.container():
        col1,col2 = st.columns(2)
        with col1:
             st.markdown('**Restaurantes com média de avaliação abaixo de 2.5**')
             df_aux = df.loc[: , ['Country','City', 'Aggregate rating']].groupby( ['Country','City']).mean().sort_values(by = 'Aggregate rating', ascending = True)
             df_aux = round(df_aux.loc[df_aux['Aggregate rating'] <= 2.5 ].reset_index(),2)
             st.dataframe(df_aux,use_container_width=True)
        with col2:
             df_aux = df.loc[: , ['Country','City', 'Aggregate rating']].groupby(['Country','City']).mean().sort_values(by = 'Aggregate rating', ascending = False)
             df_aux = round(df_aux.loc[df_aux['Aggregate rating'] >= 4.0 ].reset_index(),2).head(10)
             st.dataframe(df_aux,use_container_width=True)
             #fig = px.bar(df_aux, x= 'City', y= 'Aggregate rating', title='Restaurantes com média acima de 4 por cidade', color_continuous_scale =  px.colors.sequential.Cividis_r, height=450,width = 700 )
             #st.plotly_chart(fig, use_container_width=True)
           
     with st.container():
        col1,col2 = st.columns(2)
        with col1:     
              prato_dois = round(df.loc[ :, ['Country','City','Currency','Average Cost for two']].groupby(['Country','City', 'Currency'])
                                    .mean()
                                    .sort_values(by = 'Average Cost for two', ascending = False)
                                    .reset_index().head(10),2)
      
              fig = px.bar(prato_dois, x= 'City', y ='Average Cost for two', color = 'Currency', title='Cidades com maior peço médio de pratos para dois', color_continuous_scale = px.colors.sequential.Cividis_r, height=450,width = 700)
              st.plotly_chart(fig, use_container_width=True) 
  
        with col2:
                df_aux = df.loc[:, ['Country', 'City', 'Cuisines']].groupby(['Country', 'City']).nunique().sort_values(by = 'Cuisines', ascending= False).head(5).reset_index()
            
                fig = px.pie(df_aux,values = 'Cuisines', names = 'City', title = 'Cidades com maior tipo de culinária distintas',color_discrete_sequence=px.colors.sequential.RdBu, height=500,width = 600)
                st.plotly_chart(fig, use_container_width = True)
      


