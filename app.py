
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

# Read uploaded file with comma as decimal separator
@st.cache_data(ttl=600)
def load_data(sheets_url):
    csv_url = sheets_url.replace('/edit#gid=', '/export?format=csv&gid=')
    return pd.read_csv(csv_url, decimal=',')


#load the data
data = load_data(st.secrets["public_gsheets_url"])

# Convert "Date" column to datetime format
data['Data'] = pd.to_datetime(data['Data'],format="%d/%m/%Y")

# Set page title
st.title('Monitoraggio PacchiaHouse')

#filters sidebar creation 
st.sidebar.subheader('Filtri')
selected_fascia = st.sidebar.selectbox('Seleziona fascia',['PICCO','FUORI','TOTALE'])

# Filter data based fascia 
if selected_fascia == "TOTALE":
    filtered_data = data
else:
    filtered_data = data[data['fascia']==selected_fascia]

##### aggregations ####

# Group by month 
energia_utilizzata_fv = filtered_data.groupby('mese')['Energia utilizzata fotovoltaico ora'].sum()

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




# Plot aggregated energia utilizzata fv using Plotly
st.subheader('Energia utilizzata fotovoltaico mese')
fig = px.bar(energia_utilizzata_fv)
st.plotly_chart(fig)


# Plot aggregated data using Plotly
st.subheader('Costo con e senza pannello mese')
fig5 = px.bar(costo_energia_mese, barmode= 'group')
st.plotly_chart(fig5)

    
# Plot aggregated data using Plotly
st.subheader('Costo con e senza pannello giorno')
fig3 = px.line(costo_energia)
st.plotly_chart(fig3)

# Plot stacked bar chart using Plotly
st.subheader('% Ripartizione utilizzo e immissione in rete mese')
fig2 = px.bar(ripartizione_prod_immessa[['Percentage_energia_utilazzata','Percentage_energia_immessa']], barmode='stack')
st.plotly_chart(fig2)
        

# Plot stacked bar chart using Plotly
st.subheader('% Ripartizione utilizzo e immissione in rete (giorno)')
fig4 = px.bar(ripartizione_prod_immessa_giorno[['Percentage_energia_utilazzata','Percentage_energia_immessa']], barmode='stack')
st.plotly_chart(fig4)

       





