import streamlit as st
import pandas as pd
import plost
import numpy as np
import folium
from streamlit_folium import st_folium

def display_map(df,df2):
    #df = df[df['Publication Date'].dt.year == year]
    df['new_index'] = range(1, len(df) + 1)
    
    map= folium.Map([0,0], scrollWheelZoom= False ,tiles='cartodbpositron', zoom_start=3)

    chropleth = folium.Choropleth(
        geo_data = 'world-administrative-boundaries.geojson',
        name = 'choropleth',
        data = df,
        columns = ['country', 'Number of Claims'],
        key_on = 'feature.properties.name',
        fill_color = 'YlGn',
        fill_opacity = 0.7,
        line_opacity = 0.2,
        legend_name = 'Number of Claims',
        highlight = True
    )
    chropleth.geojson.add_to(map)


    df = df.set_index('country')
    #country_name= 'Finland'
    #st.write(df.loc[country_name,'Number of Claims'])

    for feature in chropleth.geojson.data['features']:
        country_name = feature['properties']['name']
        feature['properties']['claims'] = 'Claims: ' + str('{:,}'.format(df.loc[country_name,'Number of Claims']) if country_name in list(df.index) else 'N/A')
        feature['properties']['date_diff'] = 'Average Patent Process (days): ' + str('{:,}'.format(df2.loc[country_name,'date_diff']) if country_name in list(df2.index) else 'N/A')

    chropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name','claims','date_diff'], labels=False)
    )
    st_map=st_folium(map, width=1000, height=600)



st.set_page_config(layout='wide', initial_sidebar_state='expanded')

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    
st.sidebar.header('Filter')
year_list= [2018, 2017, 2019, 2021, 2022, 2020, 2023, 2012, 2015]
year_list.sort()
year= st.sidebar.multiselect('Year Filter', year_list, [2020,2021,2022])


#Load Data
df= pd.read_excel('tes1.xlsx')
df=df.loc[df['File series'].isin(year)]

#Filter Negara
graph_list= list(df['country'].unique())
graph_list.sort()
country= st.sidebar.multiselect('Country filter', graph_list, ['Indonesia','United States of America','Japan'])


#Data buat selisih hari
df_date_diff = df[["country","date_diff"]]
df_date_diff=df_date_diff.groupby(['country']).mean().round(0)
df_date_diff=df_date_diff.astype(int)


#Data buat jumlah paten per negara
df_edit= df.groupby(['country']).sum()
df_edit = df_edit.drop('Unnamed: 0', axis=1)
df_edit1=df_edit.drop('File series', axis=1)
df_edit2=df_edit1.drop('date_diff', axis=1)
df_reset_indexed = df_edit2.reset_index()


#Jumlah total Paten
total_claims = df_reset_indexed['Number of Claims'].sum()
indo_df = df_reset_indexed[df_reset_indexed['country'] == 'Indonesia']
indo_claims= indo_df['Number of Claims'].sum()
asing_claims=total_claims-indo_claims

#Jumlah Negara yang daftar Paten
country_count=df_date_diff.shape[0]

#Rata-Rata Proses waktu Negara Indo
df_date = df[["Unnamed: 0","country","date_diff"]]
df_date=df_date.set_index('Unnamed: 0')

indo_df_day = df_date[df_date['country'] == 'Indonesia']
indo_average= indo_df_day['date_diff'].mean()
indo_average=int(indo_average)
    
#Rata-Rata Proses waktu Negara Luar
other_df_delay= df_date[df_date['country'] != 'Indonesia']
other_average= other_df_delay['date_diff'].mean()
other_average=int(other_average)


# Row 1
st.markdown('### Jumlah Klaim Paten')
col1, col2, col3 = st.columns(3)
col1.metric("Total Klaim Paten", '{:,}'.format(total_claims), "")
col2.metric("Total Klaim Indonesia", '{:,}'.format(indo_claims), "")
col3.metric("Total Klaim Negara Asing", '{:,}'.format(asing_claims), "")

# Row 2
st.markdown('### Proses Waktu Paten')
col1, col2 = st.columns(2)
col1.metric("Rata-Rata Waktu Proses Paten di Indonesia", str('{:,}'.format(indo_average)+' Hari'))
col2.metric("Rata-Rata Waktu Proses Paten di Negara Asing",str('{:,}'.format(other_average)+' Hari'))


df_country=df_date.loc[df_date['country'].isin(country)]
df_country=df_country.groupby(['country']).mean().round()
df_country=df_country.astype(int)
df_country=df_country.abs()

# Row 3
st.markdown('### Bar Chart Waktu Proses Paten')
st.bar_chart(df_country)

#Map
display_map(df_reset_indexed,df_date_diff)

st.sidebar.markdown('''
---
Created by Adam Baihaqi.
''')


