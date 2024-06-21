import streamlit as st
import pandas as pd
import numpy as np



# Ajustar la configuración de la página de Streamlit
st.set_page_config(
    page_title="High Frequency Checks Dashboard",
    layout="wide"
)

# Título de la aplicación
st.title("High Frequency Checks Dashboard")

# Enlace al archivo CSV en Dropbox
dropbox_url = 'https://www.dropbox.com/scl/fi/yzxvmu40j45utunxnqahd/ElS-ElSalvadorDocentes_27jun2023_Final.csv?rlkey=ewchky7rm9it9obsboq8v9ls4&dl=1'

# Leer el archivo CSV desde Dropbox
data = pd.read_csv(dropbox_url)

# Crear pestañas en Streamlit
tabs = st.tabs(["High Frequency Checks", "Análisis Interactivo"])

with tabs[0]:
    # Mostrar los datos en una tabla
    st.write("Datos cargados desde Dropbox:")
    st.write(data)

    # Verificación 1: Duración de las entrevistas
    data['Duration'] = pd.to_timedelta(data['Duration'], errors = 'coerce')
    duration_check = data[(data['Duration'] < '00:05:00') | (data['Duration'] > '01:00:00')]
    st.write("Entrevistas con duración fuera del rango razonable (5 min - 1 hr):")
    st.write(duration_check)

    # Verificación 2: Ubicaciones válidas
    data['Latitude'] = pd.to_numeric(data['Latitude'], errors='coerce')
    data['Longitude'] = pd.to_numeric(data['Longitude'], errors='coerce')
    location_check = data[data['Latitude'].isnull() | data['Longitude'].isnull()]
    st.write("Registros con ubicaciones inválidas:")
    st.write(location_check)

    # Verificación 3: Estados de las encuestas
    status_check = data[data['Status'] == 'Requires Approval']
    st.write("Encuestas que requieren aprobación:")
    st.write(status_check)

    # Verificación 4: Duplicados
    duplicate_check = data[data.duplicated()]
    st.write("Registros duplicados:")
    st.write(duplicate_check)

    # Mostrar gráficos
    st.line_chart(data[['Duration']].apply(lambda x: x.dt.total_seconds()))
    data.rename(columns = {'Latitude': 'lat', 'Longitude': 'lon'}, inplace = True)
    st.map(data[['lat', 'lon']].dropna())


