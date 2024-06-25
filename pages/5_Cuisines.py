#Importando pacotes 

import pandas as pd
import plotly as py
import plotly.express as px
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

cuisines_options = st.sidebar.multiselect(
  'Selecione a Culinária de interesse:',
  ['Italian', 'European', 'Filipino', 'American', 'Korean', 'Pizza',
       'Taiwanese', 'Japanese', 'Coffee', 'Chinese', 'Seafood',
       'Singaporean', 'Vietnamese', 'Latin American', 'Healthy Food',
       'Cafe', 'Fast Food', 'Brazilian', 'Argentine', 'Arabian', 'Bakery',
       'Tex-Mex', 'Bar Food', 'International', 'French', 'Steak',
       'German', 'Sushi', 'Grill', 'Peruvian', 'North Eastern',
       'Ice Cream', 'Burger', 'Mexican', 'Vegetarian', 'Contemporary',
       'Desserts', 'Juices', 'Beverages', 'Spanish', 'Thai', 'Indian',
       'Mineira', 'BBQ', 'Mongolian', 'Portuguese', 'Greek', 'Asian',
       'Author', 'Gourmet Fast Food', 'Lebanese', 'Modern Australian',
       'African', 'Coffee and Tea', 'Australian', 'Middle Eastern',
       'Malaysian', 'Tapas', 'New American', 'Pub Food', 'Southern',
       'Diner', 'Donuts', 'Southwestern', 'Sandwich', 'Irish',
       'Mediterranean', 'Cafe Food', 'Korean BBQ', 'Fusion', 'Canadian',
       'Breakfast', 'Cajun', 'New Mexican', 'Belgian', 'Cuban', 'Taco',
       'Caribbean', 'Polish', 'Deli', 'British', 'California', 'Others',
       'Eastern European', 'Creole', 'Ramen', 'Ukrainian', 'Hawaiian',
       'Patisserie', 'Yum Cha', 'Pacific Northwest', 'Tea', 'Moroccan',
       'Burmese', 'Dim Sum', 'Crepes', 'Fish and Chips', 'Russian',
       'Continental', 'South Indian', 'North Indian', 'Salad',
       'Finger Food', 'Mandi', 'Turkish', 'Kerala', 'Pakistani',
       'Biryani', 'Street Food', 'Nepalese', 'Goan', 'Iranian', 'Mughlai',
       'Rajasthani', 'Mithai', 'Maharashtrian', 'Gujarati', 'Rolls',
       'Momos', 'Parsi', 'Modern Indian', 'Andhra', 'Tibetan', 'Kebab',
       'Chettinad', 'Bengali', 'Assamese', 'Naga', 'Hyderabadi', 'Awadhi',
       'Afghan', 'Lucknowi', 'Charcoal Chicken', 'Mangalorean',
       'Egyptian', 'Malwani', 'Armenian', 'Roast Chicken', 'Indonesian',
       'Western', 'Dimsum', 'Sunda', 'Kiwi', 'Asian Fusion', 'Pan Asian',
       'Balti', 'Scottish', 'Cantonese', 'Sri Lankan', 'Khaleeji',
       'South African', 'Drinks Only', 'Durban', 'World Cuisine',
       'Izgara', 'Home-made', 'Giblets', 'Fresh Fish', 'Restaurant Cafe',
       'Kumpir', 'Döner', 'Turkish Pizza', 'Ottoman', 'Old Turkish Bars',
       'Kokoreç'],
  default= ['Italian', 'American', 'Brazilian'])

st.sidebar.markdown('#### Powered by Umpozzobom')
st.sidebar.markdown("""___""")


#===========================================================================================#
#     LAYOUT DO STREMEALIT - criação das tabs com as informações a serem apresentadas       #
#===========================================================================================#
tab1,tab2= st.tabs (['Cuisines', '--'])  

with tab1:
     with st.container():
                 
              st.markdown ("##### Valor médio de um prato para duas pessoas por tipo de Culinária e País")
              result = (df.loc[: , ['Country','Restaurant Name','Cuisines','Currency','Average Cost for two']]
                  .sort_values(by = 'Average Cost for two', ascending = False)
                  .reset_index())
    
              df_aux01 = result.loc[result['Country']=='Australia',:].head(1)
              df_aux02 = result.loc[result['Country']=='Indonesia',:].head(1)
              df_aux03 = result.loc[result['Country']=='Brazil',:].head(1)
              df_aux04 = result.loc[result['Country']=='New Zeland',:].head(1)
              df_aux05 = result.loc[result['Country']=='Turkey',:].head(1)
              df_aux06 = result.loc[result['Country']=='England',:].head(1)
              
              df_aux07 = result.loc[result['Country']=='Philippines',:].head(1)
              df_aux08 = result.loc[result['Country']=='United States of America',:].head(1)
              df_aux09 = result.loc[result['Country']=='Canada',:].head(1)
              df_aux10 = result.loc[result['Country']=='Singapure',:].head(1)
              df_aux11 = result.loc[result['Country']=='United Arab Emirates',:].head(1)
              df_aux12 = result.loc[result['Country']=='India',:].head(1)
              
              df_aux13 = result.loc[result['Country']=='Sri Lanka',:].head(1)
              df_aux14 = result.loc[result['Country']=='Quatar',:].head(1)
              df_aux15 = result.loc[result['Country']=='South Africa',:].head(1)
              
              df3 = round(pd.concat([df_aux01,df_aux02, df_aux03,df_aux04,df_aux05,df_aux06,df_aux07,df_aux08,df_aux09,df_aux10,df_aux11,df_aux12,df_aux13,df_aux14,df_aux15]).reset_index(drop=True),2)
              st.table(df3)

     with st.container(): 
             st.markdown ('##### Maiores médias de avaliação por tipo culinária (Italian, American, Arabian, Japanese) e restaurante')
             col1,col2 = st.columns(2)

             with col1:
                  df_aux = df.loc[df['Cuisines'] == 'Italian', : ]
                  df_aux01 = (df_aux.loc[ : , ['Country', 'City','Restaurant ID','Restaurant Name', 'Cuisines','Aggregate rating']]
                                    .groupby(['Country', 'City','Restaurant ID', 'Restaurant Name', 'Cuisines',])
                                    .mean().sort_values(by = ['Aggregate rating', 'Restaurant ID'],ascending =[False, True]).head(1).reset_index()) 
                  st.table(df_aux01)
               
             with col2:
                  df_aux_american = df.loc[df['Cuisines'] == 'American', : ]
                  df_aux01 = (df_aux_american.loc[ : , ['Country', 'City','Restaurant ID','Restaurant Name', 'Cuisines','Aggregate rating']]
                                   .groupby(['Country', 'City','Restaurant ID', 'Restaurant Name', 'Cuisines'])
                                   .mean()
                                   .sort_values(by=['Aggregate rating', 'Restaurant ID'], ascending = [False, True]).head(2).reset_index())
                  st.table(df_aux01)

     with st.container(): 
             col1,col2 = st.columns(2)        
             with col1:
               df_arabian = df.loc[df['Cuisines'] == 'Arabian' , :]
               df_aux01 = (df_arabian.loc[: , ['Country', 'City','Restaurant ID','Restaurant Name', 'Cuisines','Aggregate rating']].sort_values(by = ['Aggregate rating', 'Restaurant ID'], ascending = [False, True]).head(1))
               st.table(df_aux01)

             with col2:
               df_japones = df.loc[df['Cuisines'] == 'Japanese' , :]
               df_aux01 = (df_japones.loc[: , ['Country', 'City','Restaurant ID','Restaurant Name', 'Cuisines','Aggregate rating']]
           .sort_values(by =['Aggregate rating','Restaurant ID'], ascending = [False, False]).head(1))
               st.table(df_aux01)

     with st.container(): 
             col1,col2 = st.columns(2) 
             with col1:
                st.markdown ('##### Tipo de culinária com a maior quantidade de votos e Nota de avaliação')
                df_aux = (df.loc[ :,['Restaurant ID','Cuisines', 'Votes', 'Aggregate rating']]
                            .groupby(['Restaurant ID','Cuisines', 'Votes']).median()        
                            .sort_values(by = ['Aggregate rating', 'Votes', 'Restaurant ID'], ascending = [False, False, True])
                            .head(5).reset_index()) 
                st.table(df_aux)




