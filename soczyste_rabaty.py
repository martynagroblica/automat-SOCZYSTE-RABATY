# -*- coding: utf-8 -*-
"""Soczyste rabaty.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bfU5lwdNa2GOPWmQ9-URaf30VnlBzQC0
"""

#importowanie potrzebnych bibliotek
import os
import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import io



st.set_page_config(page_title='Automat - soczyste rabaty', layout='wide')


tabs_font_css = """
<style>
div[class*="stTextInput"] label {
  font-size: 26px;
  color: black;
}
div[class*="stSelectbox"] label {
  font-size: 26px;
  color: black;
}
</style>
"""

st.write(tabs_font_css, unsafe_allow_html=True)

df = st.file_uploader(
    label = "Wrzuć plik Cykl - soczyste rabaty"
)

if df:
    df = pd.read_excel(df, sheet_name = 'Promocje na utrzymanie i FUS', skiprows = 15, usecols = [1,2,9,10])
    st.write(df.head())


#wczytanie pliku z komputera


#df = pd.read_excel(file_path, sheet_name = sheet_name, skiprows=15, usecols = [1,2,9,10])

#df

#usuń braki danych z Kod klienta
df = df.dropna(subset=['Kod klienta'])

# klient na całkowite
df['KLIENT'] = df['KLIENT'].astype(int)
df['Kod klienta'] = df['Kod klienta'].astype(int)

# Zmiana nazw kolumn
df = df.rename(columns={'0.12.1': '12', '0.14.1': '14'})

#df

# Dodaj kolumnę 'SIECIOWY', która będzie zawierać 'SIECIOWY' jeśli w kolumnach '12' lub '14' jest słowo 'powiązanie'
df['SIECIOWY'] = df.apply(lambda row: 'SIECIOWY' if 'powiązanie' in str(row['12']).lower() or 'powiązanie' in str(row['14']).lower() else '', axis=1)

#df

#SPRAWDZENIE CZY DZIAŁA
#df[df['SIECIOWY'] == 'SIECIOWY']
#DZIAŁA :)

# Funkcja do wyodrębnienia wartości procentowej
def extract_percentage(text):
    import re
    match = re.search(r'(\d+,\d+|\d+)%', text)
    return match.group(0) if match else ''

# Zastosowanie funkcji do kolumn '12' i '14'
df['12_percent'] = df['12'].apply(extract_percentage)
df['14_percent'] = df['14'].apply(extract_percentage)

#df

# Funkcja do konwersji wartości procentowej na float
def percentage_to_float(percentage_str):
    if pd.isna(percentage_str) or not percentage_str:
        return 0.0  # Zmieniono na 0.0, aby brakujące wartości były traktowane jako 0
    # Zamiana przecinka na kropkę, usunięcie znaku '%'
    return float(percentage_str.replace(',', '.').replace('%', ''))

# Konwersja kolumn '12_percent' i '14_percent' na liczby zmiennoprzecinkowe
df['12_percent'] = df['12_percent'].apply(percentage_to_float)
df['14_percent'] = df['14_percent'].apply(percentage_to_float)

# Dodaj nową kolumnę 'max_percent' z maksymalnymi wartościami z kolumn '12_percent' i '14_percent'
df['max_percent'] = df[['12_percent', '14_percent']].max(axis=1)

#df

# Wybierz wiersze, gdzie 'max_percent' nie jest równa 0
filtered_df = df[df['max_percent'] != 0]

standard = filtered_df[filtered_df['SIECIOWY'] != 'SIECIOWY']
powiazanie = filtered_df[filtered_df['SIECIOWY'] == 'SIECIOWY']

#len(standard), len(powiazanie), len(filtered_df)

standard_ost = standard[['Kod klienta', 'max_percent']]
#standard_ost

powiazanie = powiazanie[['KLIENT','Kod klienta','max_percent']]
#powiazanie




#TERAZ IMS

ims = st.file_uploader(
    label = "Wrzuć plik ims_nhd"
)

if ims:
    ims = pd.read_excel(ims, usecols=[0,2,21])
    st.write(ims.head())

ims = ims[ims['APD_Czy_istnieje_na_rynku']==1]

#ims_path = r'C:\Users\mgroblica\Neuca S.A\Obszar Doskonalenia Procesow - Dokumenty\MONITORINGI AUTOMATY\Cykle - pliki źródłowe\ims_nhd.xlsx'

#ims = pd.read_excel(ims_path, usecols=[0,2,21])


#ims

wynik_df = pd.merge(powiazanie, ims, left_on='KLIENT', right_on='Klient', how='left')
#wynik_df

# Wybór potrzebnych kolumn: 'APD_kod_SAP_apteki' i 'max_percent'
wynik_df = wynik_df[['KLIENT','APD_kod_SAP_apteki', 'max_percent']]
wynik_df

#print(wynik_df)

#to są kody SAP
wynik_df1 = wynik_df.rename(columns={'APD_kod_SAP_apteki': 'Kod klienta'})
wynik_df1 = wynik_df1[['Kod klienta','max_percent']]
#wynik_df1

#to są kody powiazan
wynik_df2 = wynik_df.rename(columns={'KLIENT': 'Kod klienta'})
wynik_df2 = wynik_df2[['Kod klienta','max_percent']]
#wynik_df2

#POŁĄCZYĆ wynik_df z standard_ost
polaczone = pd.concat([standard_ost, wynik_df1, wynik_df2], axis = 0)
#polaczone

posortowane = polaczone.sort_values(by='max_percent', ascending=False)
#posortowane

ostatecznie = posortowane.drop_duplicates(subset='Kod klienta')
#ostatecznie



#st.download_button('Pobierz wynik', ostatecznie)

excel_file = io.BytesIO()
with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
    ostatecznie.to_excel(writer, index=False, sheet_name='Sheet1')
excel_file.seek(0)  # Resetowanie wskaźnika do początku pliku

# Umożliwienie pobrania pliku Excel
st.download_button(
    label='Pobierz wynik Excel',
    data=excel_file,
    file_name='wynik.xlsx',
    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
)

