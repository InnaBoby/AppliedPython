import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import asyncio
from func import *

st.title('Анализ температурных данных и мониторинг текущей температуры через OpenWeatherMap API')
st.header('Шаг 1: Загрузка данных')

data=st.file_uploader('Выберите файл:', type=['csv'])
if data is not None:
    data=pd.read_csv(data)
    st.dataframe(data.head())


    st.header('Шаг 2: Визуализация данных')
    city=st.selectbox("ВЫберите город",
                    list(data['city'].unique()),
                    )
    df=analizer(data, city)
    #выбор параметра по которому отобразить график (мультичойс)
    if st.toggle(f"Показать график температуры для города {city}"):
        options = ["Температура", "Скользящее среднее за 30 дней", "Скользящее среднее +/- 2 сигмы", "Выбросы"]
        selection = st.pills("График", options, selection_mode="multi")
        st.text([1 if x in selection else 0 for x in options])
        st.write(plot(df, city, *[1 if x in selection else 0 for x in options]))

    if st.toggle(f"Показать профиль сезонов для города {city}"):
        st.write(get_season_profile(df, city))

    if st.toggle(f"Показать аномалии по сезонам"):
        st.write(outlaers_by_season(df, city))


    st.header('Шаг 3: Загрузка текущей температуры')
    API_KEY=st.text_input('Введите API ключ')
    try:
        if API_KEY:
            response = asyncio.run(wether_in_city(city, API_KEY))
            st.metric(label=f"Сейчас в {city}", value=response['main']['temp'])
            st.write(anomaly_detecter(df, city, API_KEY))
            if st.toggle(f"Показать подробные данные  погоде"):
                st.write(response)
    except Exception as e: 
        st.write(e)

else:
    st.write('Загрузите файл')