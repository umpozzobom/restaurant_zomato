#Importando pacotes 

import pandas as pd
import plotly.express as px
import plotly as py
from haversine import haversine
from PIL import Image
import streamlit as st
from streamlit_folium import folium_static
import folium
from folium.plugins import MarkerCluster

#Crio uma página no stremlit onde será configurado as ações
#Chamo a página no terminal -> streamlit run 

st.set_page_config(page_title='Visão Geral', page_icon=':)', layout = 'wide')

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

st.sidebar.markdown('# Restaurantes')
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
tab1,tab2= st.tabs (['Restaurantes','--'])  

with tab1:
    with st.container():
       col1,col2,col3 = st.columns(3)
       #st.header('Restaurant unique')
       with col1:
          cols = ['Restaurant Name', 'Votes']
          df_01 = df[cols].sort_values(by = ['Votes'], ascending = False).head(5)
          st.markdown('**Restaurantes com maior quantidade de Avaliações**')
          col1.table(df_01)
          
       with col2:
          df_02 = round(df.loc[: , ['Restaurant Name','Aggregate rating']].sort_values(by = [ 'Aggregate rating', 'Restaurant Name'], ascending = [False,True]).head(5),2)
          st.markdown('**Restaurantes com maior nota média**')
          col2.table(df_02)
          
       with col3:
            df_03 = (df.loc[ : , ['Restaurant Name','Currency','Average Cost for two']]
                       .groupby(['Restaurant Name','Currency',])
                       .mean()
                       .sort_values(by = 'Average Cost for two', ascending = False).head(5).reset_index())
            st.markdown('**Restaurantes com maior valor de prato para dois**')
            col3.table(df_03)

    with st.container():
        col1,col2 = st.columns(2)
        with col1:
              df_aux = df.loc[df['Country'] == 'Brazil', :]
              
              df2= (df_aux.loc[df['Cuisines']=='Brazilian', ['City','Restaurant Name', 'Aggregate rating']]
                          .sort_values(by = ['Aggregate rating'], ascending = False))
              
              #Separei a media pelas cidades, pq faz mais sentido
              
              df_aux01 = df2.loc[df2['City']== 'Brasília', :].head(3)
              df_aux02 = df2.loc[df2['City']== 'São Paulo', :].head(3)
              df_aux03 = df2.loc[df2['City']== 'Rio de Janeiro', :].head(3)
              
              df3 = pd.concat([df_aux03, df_aux02,df_aux01]).reset_index(drop=True)
              st.markdown('**Melhores restaurantes brasileiros de acordo com a avaliação média por cidade**')
              col1.table(df3)
        with col2:
            df_aux = df.loc[df['Country'] == 'Brazil', :]

            df2= (df_aux.loc[df['Cuisines']=='Brazilian', ['City','Restaurant Name', 'Aggregate rating']]
                        .sort_values(by = ['Aggregate rating'], ascending = False).head(10))

            fig = px.line(df2, x = 'Restaurant Name', y = 'Aggregate rating', labels={
                           'Aggregate rating': 'Melhores Avaliações',
            'Restaurant Name': 'Restaurantes'}, markers = True, title = '*Top 10 melhores restaurantes brasileiros', height=350,width = 700 )
         
            st.plotly_chart(fig, use_container_width=True) 


            





        