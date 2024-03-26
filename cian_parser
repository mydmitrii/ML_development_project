# функция скачивания json файла написанная на основе cURL команды и конвертации в Python

# команда search-offers-desktop запускается при переходе на каждую новую страницу сайта используя json запрос с разницей в номере страницы
# добавим в функцию номер страницы

def get_json(page_number):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    json_data = {
        'jsonQuery': {
            '_type': 'flatsale',
            'engine_version': {
                'type': 'term',
                'value': 2,
            },
            'region': {
                'type': 'terms',
                'value': [
                    1,
                    4593,
                ],
            },
            'foot_min': {
                'type': 'range',
                'value': {
                    'lte': 30,
                },
            },
            'only_foot': {
                'type': 'term',
                'value': '2',
            },
            'room': {
                'type': 'terms',
                'value': [
                    1, # где 1-3 это число комнат, для студии - число 9
                ],
            },
            'building_status': {
                'type': 'term',
                'value': 2,
            },
            'only_flat': {
                'type': 'term',
                'value': True,
            },
            'from_developer': {
                'type': 'term',
                'value': True,
            },
            'page': {
                'type': 'term',
                'value': page_number, # изменяемый параметр в зависимости от открытой страницы
            },
        },
    }
    response = requests.post(
        'https://api.cian.ru/search-offers/v2/search-offers-desktop/',
        headers=headers,
        json=json_data,
    )
    json_data = response.json()
    return json_data


# Для скачивания данных со всех страниц, будем проходиться по страницам используя библиотеку Selenium
# Cкачивать при помощи функции get_json значения с search-offers-desktop для каждой открытой страницы    

# инициализация драйвера браузера

# путь к драйверу Chrome
webdriver_service = Service('C:\\Windows\\chromedriver.exe')

# создание нового экземпляра драйвера Chrome
options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36")
options.add_argument("--disable-blink-features")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-plugins-discovery")

driver = webdriver.Chrome(service=webdriver_service, options=options)
driver.set_window_size(1366, 768)  # установка размеров окна браузера

# открытие страницы.
# указываем ссылку на страницу поиска. В зависимости от 1-комн, 2-комн. квартиры и т.д., ссылка будет разная
driver.get('https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&foot_min=30&from_developer=1&object_type%5B0%5D=2&offer_type=flat&only_flat=1&only_foot=2&region=-1&room1=1')

data = []  # список для хранения данных
error_pages = []  # список для хранения страниц с ошибками

# количество скачанных страниц ЦИАН
# фильтр Циана не дает скачать более 1500 данных и ограничивает поиск всегда на 54-55 странице, поэтому ограничим число страниц 55
num_pages = 55

for i in range(num_pages):
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Дальше')]")) # ищем кнопку "Дальше", которая запускает search-offers-desktop
        )

        if element is None:
            print(f"No more pages found after page {i}. Stopping...")
            break

        # вызов функции get_json() для скрапинга данных
        offers = get_json(i+1)
        data.extend(offers.get('data', {}).get('offersSerialized', []))

        print(f"Страница скачана: {i+1}")

        next_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Дальше')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        time.sleep(1)

        driver.execute_script("arguments[0].click();", next_button)

        time.sleep(random.uniform(3,8)) # сделаем рандомное время паузы

    except Exception as e:
        error_pages.append(i + 1)
        continue

# закрытие браузера
driver.quit()

# сохранение данных без ошибок в JSON-файл
filepath = "D:/Docs/Python/cian_df/data.json"

data_without_errors = [data[i] for i in range(len(data)) if i not in error_pages]

with open(filepath, 'w') as json_file:
    json.dump(data_without_errors, json_file)                  
