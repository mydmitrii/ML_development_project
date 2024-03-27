# Полученный парсингом JSON файл представляет собой мешанину в одну строку, которую невозможно использовать. 
# Поэтому необходимо написать функцию для сборки признаков необходимых для датасета и игнорирования тех признаков, которые не нужны и конструирования из них датафреймов

# Функция для сборки необходимых признаков для датасета
def get_offer(item):

    offer = {}
    offer["url"] = item["fullUrl"] # ссылка на сайт
    offer["offer_id"] = item["id"] # номер объявления
    offer["address"] = item["geo"]["userInput"] # адресс

    # изменим дату объявления, чтобы год был в начале
    timestamp = datetime.fromtimestamp(item["addedTimestamp"])
    timestamp = datetime.strftime(timestamp, '%Y-%m-%d %H:%M:%S')
    offer["offer_date"] = timestamp # дата публикации

    # соберем признаки объявления
    offer["price"] = item["bargainTerms"]["priceRur"] # цена
    offer["area"] = item["totalArea"] # общая площадь
    offer["rooms"] = item["roomsCount"] # число комнат

    # дата окончания строительства
    # дата окончания строительства есть не у всех значений
    if item.get("building") and item["building"].get("deadline") and item["building"]["deadline"].get("quarterEnd"):
        offer["release_date"] = item["building"]["deadline"]["quarterEnd"]
    # если есть только год, то дата окончания будет "год"+середина года (2 июля)
    elif item.get("building") and item["building"].get("deadline") and item["building"]["deadline"].get("year"):
        year = item["building"]["deadline"]["year"]
        offer["release_date"] = f"{year}-07-02"
    # если года нет, то напишем "no data"
    else:
        offer["release_date"] = "no data"  # значение по умолчанию, если нет данных о дедлайне

    # материал стен
    offer["materialType"] = item["building"]["materialType"]

    # отделка квартиры
    # для тех квартир у кого не прописана отделка напишем "без отделки"
    if item.get("decoration") is None:
       offer["decoration"] = "without"
    else:
        offer["decoration"] = item["decoration"]

    # этажи
    offer["floor"] = item["floorNumber"] # номер этажа
    offer["total_floor"] = item["building"]["floorsCount"] # общее число этажей

    # паркинг
    if "building" in item and item["building"].get("parking") is not None:
        offer["parking"] = item["building"]["parking"]["type"]
    else:
        offer["parking"] = "no parking" # значение по умолчанию, если нет данных о паркинге


    # географические координты
    offer["geo_longitude"] = item["geo"]["coordinates"]["lng"] # долгота
    offer["geo_latitude"] = item["geo"]["coordinates"]["lat"] # широта


    # id станции метро и время пешком до него
    for i, underground in enumerate(item["geo"]["undergrounds"]):

        # оcтавим только расстояние пешком до метро
        if underground["transportType"] == "walk":
            underground_id = underground["id"]
            time = underground["time"]

            # оcтавим 2 столбца с ближайшими метро пешком и временем до него
            if i == 0:
                offer["metro_1_id"] = underground_id
                offer["time_to_metro_1"] = time
            elif i == 1:
                offer["metro_2_id"] = underground_id
                offer["time_to_metro_2"] = time
            else:
                break

    return offer



def get_offers(data):
    # Создание пустого DataFrame
    offers_df = pd.DataFrame()

    for item in data:
        offer = get_offer(item)
        # Добавление предложения в DataFrame
        offer_df = pd.DataFrame([offer])  # преобразование словаря в DataFrame
        offers_df = pd.concat([offers_df, offer_df], ignore_index=True)

    return offers_df



df = get_offers(data_without_errors)

# сохраним df в csv-файл для дальнейшего использования:
df.to_csv(r"D:\Docs\Python\cian_df\cian_data.csv", index=False)
  
