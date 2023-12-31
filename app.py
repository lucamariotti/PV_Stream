
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from google.oauth2 import service_account
from gsheetsdb import connect

st.set_option('deprecation.showPyplotGlobalUse', False)

# Create a connection object.
credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
    ],
)

conn = connect(credentials=credentials)
sheet_url = st.secrets["private_gsheets_url"]

# Query the Google Sheet
query = f'SELECT * FROM "{sheet_url}"' 
data = pd.read_sql_query(query, conn)


# Convert "Date" column to datetime format
data['Data'] = pd.to_datetime(data['Data'],format="%d/%m/%Y")

# Set page title
st.title('Monitoraggio PacchiaHouse')

#filters sidebar creation 
st.sidebar.subheader('Filtri')
selected_fascia = st.sidebar.selectbox('Seleziona fascia',['PICCO','FUORI','TOTALE'])
selected_anno = st.sidebar.selectbox('Seleziona Anno', [2023,2024])

# Filter data based fascia 
if selected_fascia == "TOTALE":
    filtered_data = data[data['anno']==selected_anno]
else:
    filtered_data = data[(data['fascia']==selected_fascia) & (data['anno']==selected_anno)]

##### aggregations ####

# Group by month 
energia_utilizzata_fv = filtered_data.groupby('mese')['Energia utilizzata fotovoltaico ora'].sum()

# Group by month consumo_casa
consumo_casa = filtered_data.groupby('mese')['consumo casa ora'].sum()



# Costo by day split between costo con pannello e senza 
costo_energia = filtered_data.groupby('Data')[['costo con pannello','costo senza pannello']].sum()
costo_energia_mese = filtered_data.groupby('mese')[['costo con pannello','costo senza pannello']].sum()

#####


# % between production photovoltaic and grid release
ripartizione_prod_immessa = filtered_data.groupby('mese')[['Energia utilizzata fotovoltaico ora','energia immessa ora']].sum()
ripartizione_prod_immessa_giorno = filtered_data.groupby('giorno')[['Energia utilizzata fotovoltaico ora','energia immessa ora']].sum()

# Calculate percentage Overall and day of the week
total_values = filtered_data.groupby('mese')['produzione fotovoltaico ora'].sum()
ripartizione_prod_immessa['Percentage_energia_utilazzata'] = ripartizione_prod_immessa['Energia utilizzata fotovoltaico ora'] / total_values * 100
ripartizione_prod_immessa['Percentage_energia_immessa'] = ripartizione_prod_immessa['energia immessa ora'] / total_values * 100

# 

total_values_day = filtered_data.groupby('giorno')['produzione fotovoltaico ora'].sum()
ripartizione_prod_immessa_giorno['Percentage_energia_utilazzata'] = ripartizione_prod_immessa_giorno['Energia utilizzata fotovoltaico ora'] / total_values_day * 100
ripartizione_prod_immessa_giorno['Percentage_energia_immessa'] = ripartizione_prod_immessa_giorno['energia immessa ora'] / total_values_day * 100

months =  ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC']
# Plot aggregated energia utilizzata fv using Plotly
st.subheader('Energia utilizzata fotovoltaico mese')
fig = px.bar(energia_utilizzata_fv)
fig.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': months})
st.plotly_chart(fig)

#Plot consumo casa reale 
st.subheader('Consumo casa mese')
fig6 = px.bar(consumo_casa)
fig6.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': months})
st.plotly_chart(fig6)

# Plot aggregated data using Plotly
st.subheader('Costo con e senza pannello mese')
fig5 = px.bar(costo_energia_mese, barmode= 'group')
fig5.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': months})
st.plotly_chart(fig5)

    
# Plot aggregated data using Plotly
st.subheader('Costo con e senza pannello giorno')
fig3 = px.line(costo_energia)
st.plotly_chart(fig3)

# Plot stacked bar chart using Plotly
st.subheader('% Ripartizione utilizzo e immissione in rete mese')
fig2 = px.bar(ripartizione_prod_immessa[['Percentage_energia_utilazzata','Percentage_energia_immessa']], barmode='stack')
fig2.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': months})
st.plotly_chart(fig2)
        

# Plot stacked bar chart using Plotly
st.subheader('% Ripartizione utilizzo e immissione in rete (giorno)')
fig4 = px.bar(ripartizione_prod_immessa_giorno[['Percentage_energia_utilazzata','Percentage_energia_immessa']], barmode='stack')
fig4.update_layout(xaxis={'categoryorder': 'array', 'categoryarray': ['LUN', 'MAR', 'MER', 'GIO', 'VEN', 'SAB', 'DOM']})

st.plotly_chart(fig4)

       





