import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from tqdm import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os.path


def start_browser():
    res = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('headless')  # закомментируй, если хочется видеть браузер
        options.add_argument('--verbose')
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.set_page_load_timeout(60)
        res = driver
    except:
        pass
    return res

def clicking(driver):
    try:
        click_cookies = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div/button').click()
    except: pass
    time.sleep(0.25)
    try:
        input_cost_1 = driver.find_element(By.XPATH, '//*[@id="p-9-price_usd"]').send_keys('1')  # устанавливаем минимальную цену - '1' - для получения url
    except:
        input_cost_1 = driver.find_element(By.XPATH, '//*[@id="p-118-price_usd"]').send_keys('1') # изменилось на infinity)
    time.sleep(1)

    try:
        click_filter = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[3]/form/div/div[3]/div/div[3]/div[2]/div[2]/button/span').click()  # жмем кнопку фильтра
    except Exception as e:
        click_filter = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[4]/form/div/div[3]/div/div[3]/div[2]/div[2]/button/span').click()  # иногда меняется верстка)

def get_brands():       # парсим все бренды авто и записывем в файл 'brands.npy'
    driver = start_browser()
    driver.get("https://cars.av.by/")
    time.sleep(1)
    click_cookies = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div/button').click()
    time.sleep(0.5)
    brands_all_show = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[2]/div[2]/p/button').click()     # раскрываем списко всех брендов авто
    time.sleep(0.5)
    brands = driver.find_elements(By.CLASS_NAME, 'catalog__link')      # находим все имена брендов

    brands_list = {}
    try:
        for brand in brands:
            link = brand.get_attribute('href')   # извлекаем ссылки брендов
            name = brand.get_attribute('title')   # извлекаем имена брендов
            brands_list.update({name: link})    # добавляем в пустой список имена + ссылки
        np.save('base_data_av_by/brands.npy', brands_list)  # сохраняем все в файл
        print('OK--парсинг брендов')
    except Exception as e:
        print('ERROR--парсинг брендов', e)

def get_brands_part_url():      # Парсим номера для определения брендов авто
    brands_dict = np.load('base_data_av_by/brands.npy', allow_pickle=True).item()  # ссылаемся на файл
    driver = start_browser()

    brands_list_digits = {}
    for key in tqdm(brands_dict):
        driver.get(brands_dict[key])
        time.sleep(5)
        clicking(driver)    # Прокликиваем куки/вбиваем цену/жмем кнопку фильтра
        time.sleep(0.5)
        element = WebDriverWait(driver, 5).until(EC.text_to_be_present_in_element((By.XPATH,
        '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[2]/div/h1'), 'Автомобили')) # явное ожидание загрузки страницы (хз работает ли как надо)
        link = driver.current_url   # получаем ссылку с ввода в браузер
        current_brand = '&'.join(link.replace('https://cars.av.by/filter?brands[0][brand]=', '').split('&')[0:1])
        brands_list_digits.update({key: current_brand})  # добавляем в пустой список имена + цифры
        time.sleep(0.25)
    np.save('base_data_av_by/brands_part_url.npy', brands_list_digits)  # сохраняем все в файл

def get_models(): # парсим модели
    brands_dict = np.load('base_data_av_by/brands.npy', allow_pickle=True).item()
    driver = start_browser()
    try:
        click_cookies = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div/button').click()
    except: pass

    for key in tqdm(brands_dict):
        driver.get(brands_dict[key])
        time.sleep(7)
        models = driver.find_elements(By.CLASS_NAME, 'catalog__link')  # находим все имена моделей
        model_list = {}
        try:
            for model in tqdm(models):
                link = model.get_attribute('href')  # извлекаем ссылки брендов
                name = model.get_attribute('title')  # извлекаем имена брендов
                model_list.update({name: link})  # добавляем в пустой список имена + ссылки
            np.save(f'base_data_av_by/models/{key}.npy', model_list)  # сохраняем все в файл
        except Exception as e:
            print(f'ERROR--{key}', e)

def get_models_part_url(): # парсим номера для гет запросов
    brands_dict = np.load('base_data_av_by/brands.npy', allow_pickle=True).item()
    driver = start_browser()

    for brand in tqdm(brands_dict):
        models_file = np.load(f'models/{brand}.npy', allow_pickle=True).item()
        model_list_digits = {}
        if not os.path.exists(f'models_part_url/{brand}.npy'):
            for model in tqdm(models_file):
                driver.get(models_file[model])
                time.sleep(5)
                clicking(driver)  # Прокликиваем куки/вбиваем цену/жмем кнопку фильтра
                time.sleep(0.5)
                element = WebDriverWait(driver, 5).until(
                    EC.text_to_be_present_in_element((By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[3]/form/div/div[1]'),
                                                     'Поиск по параметрам'))  # явное ожидание загрузки страницы (хз работает ли как надо)
                link = driver.current_url  # получаем ссылку с ввода в браузер
                current_model = ('&'.join(link.replace('https://cars.av.by/filter?brands[0][brand]=', '').split('&')[1:2])).replace('brands[0][model]=', '')
                model_list_digits.update({model: current_model})  # добавляем в пустой список имена + цифры
                time.sleep(0.25)
            np.save(f'models_part_url/{brand}.npy', model_list_digits)  # сохраняем все в файл

def corerection_models():
    hyndai = np.load('models_part_url/Hyundai.npy', allow_pickle=True).item()
    hyndai['Accent'] = '434'
    hyndai['Grand Santa Fe'] = '5613'
    hyndai['Solaris'] = '2336'
    np.save(f'models_part_url/Hyundai.npy',  hyndai)
    ford = np.load('models_part_url/Ford.npy', allow_pickle=True).item()
    ford['S-MAX'] = '1949'
    np.save(f'models_part_url/Ford.npy', ford)
    vw = np.load('models_part_url/Volkswagen.npy', allow_pickle=True).item()
    vw['Polo'] = '1229'
    np.save(f'models_part_url/Volkswagen.npy', vw)
    renault = np.load('models_part_url/Renault.npy', allow_pickle=True).item()
    renault['Logan Stepway'] = '10148'
    np.save(f'models_part_url/Renault.npy', renault)


# бренд модель топливо коробка год_от год_до цена_от цена_до объем_от объем_до (пропустить параметр -> '-')
get_cars_input = 'citroen c4-picasso d a 2016 - 9000 15009 1400 2000'

def car_parturl():     # фильтр авто по запросу 'get_cars_input'. Определение запроса и использование налету

    list_param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=', 'year[max]=', 'price_usd[min]=', 'price_usd[max]=',
                        'engine_capacity[min]=', 'engine_capacity[max]=']
    car_input = dict(zip(list_param_input, get_cars_input.split(' ')))
    transmission = {'a': '1', 'm': '2'}
    motor = {'b': '1', 'bpb': '2', 'bm': '3', 'bg': '4', 'd': '5', 'dg': '6', 'e': '7'}

    if car_input['transmission_type='] == 'a':
        car_input['transmission_type='] = '1'
    else:
        car_input['transmission_type='] = '2'

    for key in motor:
        if key == car_input['engine_type[0]=']:
            car_input['engine_type[0]='] = motor[key]

    new_part = []
    for key in car_input:
        if car_input[key] != '-':
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part[2:])

    if car_input['brands[0][model]='] == '-':
        car_input['brands[0][model]='] = ''

    driver = start_browser()
    driver.get(f"https://cars.av.by/{car_input['brands[0][brand]=']}/{car_input['brands[0][model]=']}")
    time.sleep(2)
    clicking(driver)        # Прокликиваем куки/вбиваем цену/жмем кнопку фильтра
    time.sleep(0.5)
    link = driver.current_url       # получаем ссылку с ввода в браузер
    current_car = '&'.join(link.replace('https://cars.av.by/filter?', '').split('&')[0:2])      # чистим ссылку и получаем get-запроc на нашу машину

    if car_input['brands[0][model]='] == '-':
        current_car = '&'.join(link.replace('https://cars.av.by/filter?', '').split('&')[0:1])

    driver.get(f"https://cars.av.by/filter?{current_car}"+f"&{new_part_url}")
    print(20*'OK**')
    time.sleep(2)


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}

brands_link = np.load('brands.npy', allow_pickle=True).item()
brands_link.update({'Hozon': 'https://cars.av.by/hozon'})
brands_link.update({'Polestar': 'https://cars.av.by/polestar'})
brands_link.update({'Voyah': 'https://cars.av.by/voyah'})
brands_link.update({'ZX': 'https://cars.av.by/zx'})
def get_from_json_brands():
    url = 'https://api.av.by/home/filters/home/init'
    r = requests.get(url, headers=headers).json()
    brands = {}
    for car in tqdm(r['blocks'][0]['rows'][0]['propertyGroups'][0]['properties'][0]['value'][0][1]['options']):
        id = car['id']
        name = car['label']
        slug = brands_link[name].split('/')[-1]
        brands.update({name: [id, slug]})
    np.save('brands_name_id_slug.npy', brands)


def get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://api.av.by/offer-types/cars/landings/'
    brands = np.load('brands_name_id_slug.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][1]}', headers=headers).json()
        models_dict = {}
        for car in r['seo']['links']:
            name = car['label']
            try:
                rr = requests.get(f'{url}{brands[item][1]}/{name}', headers=headers).json()
                id = rr['metadata']['modelId']
            except:
                continue
            slug = car['url'].split('/')[-1]
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'brands_dict_models.npy', brand_dict)


if __name__ == '__main__':
    print(np.load('brands_name_id_slug.npy', allow_pickle=True).item())
    print(np.load('brands_dict_models.npy', allow_pickle=True).item())





