import streamlit as st
import streamlit_folium as stf
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import OrdinalEncoder
import os
from bs4 import BeautifulSoup
import folium

# загрузка моделей
with open(os.path.join(models_path, 'model_price.pkl'), 'rb') as f:
    model_price = pickle.load(f)
    
with open(os.path.join(models_path, 'model_material.pkl'), 'rb') as f:
    model_material = pickle.load(f)

with open(os.path.join(models_path, 'model_decoration.pkl'), 'rb') as f:
    model_decoration = pickle.load(f)

with open(os.path.join(models_path, 'model_parking.pkl'), 'rb') as f:
    model_parking = pickle.load(f)

# загрузка словаря метро
with open('metros-moscow-v2.xml', 'r', encoding='utf-8') as f:
    content = f.read()

soup = BeautifulSoup(content, 'lxml')


# находим все элементы 'location'
locations = soup.find_all('location')

# преобразуем содержимое в словарь
metro_dict = {}
for location in locations:
    station_name = location.text
    station_id = int(location['id'])
    metro_dict[station_name] = station_id

metro_dict = dict(sorted(metro_dict.items(), key=lambda x: x[0]))


# ввод данных пользователем
def user_input_features():
    # пропишем средние площади квартир в зависимости от комнатности
    # студия - 25 м2, 1К - 38 м2, 2К - 52 м2, 3К - 66 м2
    rooms_area = {0: 25, 1: 38, 2: 52, 3: 66} 
    floor = 12 # середина от max этажности
    total_floor = 25 # пример за среднюю этажность дома 25 этажей
    coordinates = st.text_input('Введите координаты (широта, долгота)',
                               value="55.798150, 37.430560").split(',') #формат координат Яндекс-карты
    geo_latitude = float(coordinates[0]) # широта
    geo_longitude = float(coordinates[1]) # долгота

    # проверка введенных координат
    if not 55.600000 <= geo_latitude <= 55.910000 or not 37.300000 <= geo_longitude <= 37.900000:
        st.warning('Координаты находятся за пределами Москвы. Проверьте введенные данные.')
        return None


    # выпадающий список метро
    metro_name = st.selectbox('Выберите ближайшую станцию', list(metro_dict.keys()))
    time_to_metro_1 = st.number_input('Время пешком до метро', min_value=1)
    
    
    user_data_list = []
    
    for rooms, area in rooms_area.items():
        user_data = {
            'area': area,
            'rooms': rooms,
            'floor': floor,
            'total_floor': total_floor,
            'geo_longitude': geo_longitude,
            'geo_latitude': geo_latitude,
            'metro_1_id': metro_dict[metro_name],
            'time_to_metro_1': time_to_metro_1
        }
        user_data_list.append(user_data)
    
    return pd.DataFrame(user_data_list)

st.title('Оценка участка застройки')
user_data = user_input_features()

# Displaying the folium map
m = folium.Map(location=[user_data['geo_latitude'][0], user_data['geo_longitude'][0]], zoom_start=15)
folium.Marker([user_data['geo_latitude'][0], user_data['geo_longitude'][0]]).add_to(m)
stf.folium_static(m)

# прогноз
material_prediction = model_material.predict(user_data)
decoration_prediction = model_decoration.predict(user_data)
parking_prediction = model_parking.predict(user_data)

# создание нового датафрейма с предсказанными метками
predicted_df = user_data.copy()
predicted_df['materialType'] = material_prediction
predicted_df['decoration'] = decoration_prediction
predicted_df['parking'] = parking_prediction

# кодирование предсказаний
oe = OrdinalEncoder()

predicted_df[['materialType_encoded', 'decoration_encoded', 'parking_encoded']] = oe.fit_transform(
    predicted_df[['materialType', 'decoration', 'parking']])

# подготовка данных для предсказания цены
price_df = predicted_df.drop(columns = ['materialType','decoration', 'parking'])

# Предсказание цены
price_predictions = model_price.predict(price_df)

room_types = ['студии', '1к квартиры', '2к квартиры', '3к квартиры']

for room_type, price, material_type, decoration, parking in zip(room_types, price_predictions, material_prediction, decoration_prediction, parking_prediction):
    if price > 800000:
        housing_class = 'Премиум'
    elif 400000 < price < 800000 or (material_type == 'brick' and parking == 'underground'):
        housing_class = 'Бизнес'
    else:
        housing_class = 'Комфорт'

st.markdown(f'<h4>Класс жилья</h4>', unsafe_allow_html=True)
st.write(housing_class)

st.markdown(f'<h4>Материал стен</h4>', unsafe_allow_html=True)
st.write(material_prediction[0])

st.markdown(f'<h4>Тип отделки</h4>', unsafe_allow_html=True)
st.write(decoration_prediction[0])

st.markdown(f'<h4>Тип паркинга</h4>', unsafe_allow_html=True)
st.write(parking_prediction[0])

for room_type, price in zip(room_types, price_predictions):
    st.markdown(f'<h4>Средняя цена 1 кв. м для {room_type}</h4>', unsafe_allow_html=True)
    st.write(price)
