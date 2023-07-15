$ git remote add amvera https://git.amvera.ru/drullez/ds-final-project
$ git push amvera master

import streamlit as st
import pandas as pd
import numpy as np
import pickle
from category_encoders import CatBoostEncoder

# Загрузка моделей
with open('model_price.pkl', 'rb') as f:
    model_price = pickle.load(f)
    
with open('model_material.pkl', 'rb') as f:
    model_material = pickle.load(f)

with open('model_decoration.pkl', 'rb') as f:
    model_decoration = pickle.load(f)

with open('model_parking.pkl', 'rb') as f:
    model_parking = pickle.load(f)

# Инициализация кодировщика
cbe = CatBoostEncoder()

# Ввод данных пользователем
def user_input_features():
    area = st.number_input('Area', min_value=0)
    rooms = st.number_input('Number of rooms', min_value=0)
    floor = st.number_input('Floor', min_value=0)
    total_floor = st.number_input('Total number of floors in the building', min_value=0)
    geo_longitude = st.number_input('Geographical longitude', value=0.0)
    geo_latitude = st.number_input('Geographical latitude', value=0.0)
    metro_1_id = st.number_input('Metro station ID', min_value=0)
    time_to_metro_1 = st.number_input('Time to metro station', min_value=0)
    
    user_data = {
        'Area': area,
        'Number of rooms': rooms,
        'Floor': floor,
        'Total number of floors in the building': total_floor,
        'Geographical longitude': geo_longitude,
        'Geographical latitude': geo_latitude,
        'Metro station ID': metro_1_id,
        'Time to metro station': time_to_metro_1
    }
    
    return pd.DataFrame(user_data, index=[0])

st.title('My prediction application')
user_data = user_input_features()

# Прогноз
material_prediction = model_material.predict(user_data)
decoration_prediction = model_decoration.predict(user_data)
parking_prediction = model_parking.predict(user_data)

# Кодирование предсказаний
encoded_df = pd.DataFrame(
    np.column_stack([material_prediction, decoration_prediction, parking_prediction]), 
    columns=['materialType', 'decoration', 'parking'])

encoded_df = cbe.transform(encoded_df)

# Объединение пользовательских данных и закодированных предсказаний
user_data_encoded = pd.concat([user_data, encoded_df], axis=1)

# Предсказание цены
price_prediction = model_price.predict(user_data_encoded)

st.subheader('Price prediction')
st.write(price_prediction)
