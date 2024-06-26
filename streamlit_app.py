import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Ajustar la configuración de la página de Streamlit
st.set_page_config(
    page_title="High Frequency Checks Dashboard",
    layout="wide"
)

# Título de la aplicación
st.title("High Frequency Checks Dashboard")

# Enlace al archivo CSV en Dropbox
dropbox_url = 'https://www.dropbox.com/scl/fi/pswt5c75c2o2v0csix4mr/EGRA.csv?rlkey=0qzi3sjcs4oklsuncamhz1xt7&dl=1'

# Leer el archivo CSV desde Dropbox
# @st.cache_resource
def load_data(url):
    data = pd.read_csv(url)
    return data

data = load_data(dropbox_url)

# Columnas relevantes
col = ['SubmissionDate', 'starttime', 'endtime', 'duration',
       'encuestador', 'encuestador_other', 'department',
       'School', 'School_other', 'id_estudiante_nie', 'consentimiento_oral']

# Dividir las variables en secciones
sections = {
    "Fonológica Parte 1": ['fonologica_1_1', 'fonologica_1_2', 'fonologica_1_3', 'fonologica_1_4', 'fonologica_1_5'],
    "Fonológica Parte 2": ['fonologica_2_1', 'fonologica_2_2', 'fonologica_2_3', 'fonologica_2_4', 'fonologica_2_5'],
    "Fonológica Parte 3": ['fonologica_3_1', 'fonologica_3_2', 'fonologica_3_3', 'fonologica_3_4', 'fonologica_3_5'],
    "Letras": [f'letters_{i}' for i in range(1, 101)] + ['letters_999', 'letter_time', 'letter_attempted', 'letter_incorrect', 'letters_correct', 'letters_score'],
    "Palabras No Reales": [f'nonwords_{i}' for i in range(1, 71)] + ['nonwords_999', 'nonwords_time', 'nonwords_attempted', 'nonwords_incorrect', 'nonwords_correct', 'nonwords_score'],
    "Lectura Oral": [f'reading_{i}' for i in range(1, 149)] + ['reading_999', 'reading_time', 'reading_attempted', 'reading_incorrect', 'reading_correct', 'reading_sentences', 'reading_score'],
    "Comprensión Oral": ['oral_comprehension_1', 'oral_comprehension_2', 'oral_comprehension_3', 'oral_comprehension_4', 'oral_comprehension_5', 'oral_comprehension_6', 'oral_comprehension_7', 'oral_comprehension_8', 'oral_comprehension_9', 'oral_comprehension_10', 'oral_comprehension_11'],
    "Contexto del Estudiante": [col for col in data.columns if col.startswith('context_est_')]
}

def display_category_percentages(df, variables):
    category_counts = {}
    for var in variables:
        if df[var].dtype == 'object' or len(df[var].unique()) <= 5:
            counts = df[var].value_counts(normalize=True) * 100
            category_counts[var] = counts
    category_counts_df = pd.DataFrame(category_counts).transpose()
    category_counts_df.fillna(0, inplace=True)
    return category_counts_df

def display_descriptive_stats(df, variables):
    descriptive_stats = df[variables].describe().transpose()
    return descriptive_stats

# Crear pestañas en Streamlit
tabs = st.tabs(["General", "Missing Values", "Resultados Finales"] + list(sections.keys()))

with tabs[0]:
    # Mostrar los datos en una tabla
    st.write("Datos cargados:")
    st.write(data)

    # Verificación 1: Duración de las entrevistas
    data['starttime'] = pd.to_datetime(data['starttime'], format='%d/%m/%Y, %H:%M:%S', errors='coerce')
    data['endtime'] = pd.to_datetime(data['endtime'], format='%d/%m/%Y, %H:%M:%S', errors='coerce')
    data['duration'] = (data['endtime'] - data['starttime']).dt.total_seconds() / 60  # Duración en minutos
    duration_check = data[(data['duration'] < 2) | (data['duration'] > 60)]
    st.write("Entrevistas con duración fuera del rango razonable (2 min - 1 hr):")
    st.write(duration_check[col])

    # Verificación 2: Duplicados
    duplicate_check = data[data.duplicated()]
    st.write("Registros duplicados:")
    st.write(duplicate_check[col])

with tabs[1]:
    # Analizar valores faltantes
    st.write("Análisis de Valores Faltantes")

    missing_values = data[col].isnull().sum()
    missing_percentage = (missing_values / len(data)) * 100
    missing_data = pd.DataFrame({'Total Missing': missing_values, 'Percentage Missing': missing_percentage})

    st.write("Tabla de valores faltantes:")
    st.write(missing_data)

    # Mostrar gráfico de valores faltantes
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(x=missing_data.index, y=missing_data['Total Missing'], ax=ax)
    plt.xticks(rotation=90)
    plt.ylabel("Número de valores faltantes")
    plt.title("Valores faltantes por variable")
    st.pyplot(fig)

# Crear pestañas para cada sección específica
for i, section in enumerate(sections.keys(), 3):
    with tabs[i]:
        st.write(f"Análisis de Valores Faltantes en {section}")

        variables = sections[section]
        section_missing_values = data[variables].isnull().sum()
        section_missing_percentage = (section_missing_values / len(data)) * 100
        section_missing_data = pd.DataFrame({'Total Missing': section_missing_values, 'Percentage Missing': section_missing_percentage})

        st.write(f"Tabla de valores faltantes en {section}:")
        st.write(section_missing_data)

        # Mostrar tabla de porcentajes para variables categóricas con menos de 5 categorías
        if section in ["Fonológica Parte 1", "Fonológica Parte 2", "Fonológica Parte 3", 'Letras',
                       "Palabras No Reales", "Lectura Oral", "Comprensión Oral"]:
            category_counts = display_category_percentages(data, variables)
            st.write("Porcentajes de respuestas categóricas:")
            st.write(category_counts)

# Nueva pestaña para Resultados Finales
with tabs[2]:
    st.write("Análisis Descriptivo de Variables")
    
    # Filtrar variables que contienen '_score'
    score_variables = [col for col in data.columns if '_score' in col]
    
    # Tabla descriptiva
    descriptive_stats = display_descriptive_stats(data, score_variables)
    st.write("Tabla Descriptiva:")
    st.write(descriptive_stats)
    st.write("Score = Items identified - Incorrect items/(duration - time remaining)/duration")

    # Generar gráficos para las variables '_score'
    st.write("Gráficos de Variables")
    num_vars = len(score_variables)
    fig, axes = plt.subplots(nrows=num_vars, ncols=2, figsize=(12, num_vars * 6))
    
    for idx, var in enumerate(score_variables):
        sns.histplot(data[var], bins=20, kde=True, ax=axes[idx, 0])
        axes[idx, 0].set_title(f"Distribución de {var}")
        
        sns.boxplot(data[var], ax=axes[idx, 1])
        axes[idx, 1].set_title(f"Caja y Bigotes de {var}")
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.write("Análisis Descriptivo de las Partes Fonológicas")
    
    # Sumar los puntos de cada parte fonológica
    data['fonologica_total_1'] = (data[sections['Fonológica Parte 1']] == 1).sum(axis=1)
    data['fonologica_total_2'] = (data[sections['Fonológica Parte 2']] == 1).sum(axis=1)
    data['fonologica_total_3'] = (data[sections['Fonológica Parte 3']] == 1).sum(axis=1)
    
    fonologica_totals = ['fonologica_total_1', 'fonologica_total_2', 'fonologica_total_3']
    
    # Tabla descriptiva para las partes fonológicas
    fonologica_descriptive_stats = display_descriptive_stats(data, fonologica_totals)
    st.write("Tabla Descriptiva de las Partes Fonológicas:")
    st.write(fonologica_descriptive_stats)
    
    # Generar gráficos para las partes fonológicas
    st.write("Gráficos de las Partes Fonológicas:")
    num_fonologica_vars = len(fonologica_totals)
    fig, axes = plt.subplots(nrows=num_fonologica_vars, ncols=2, figsize=(12, num_fonologica_vars * 6))
    
    for idx, var in enumerate(fonologica_totals):
        sns.histplot(data[var], bins=20, kde=True, ax=axes[idx, 0])
        axes[idx, 0].set_title(f"Distribución de {var}")
        
        sns.boxplot(data[var], ax=axes[idx, 1])
        axes[idx, 1].set_title(f"Caja y Bigotes de {var}")
    
    plt.tight_layout()
    st.pyplot(fig)
