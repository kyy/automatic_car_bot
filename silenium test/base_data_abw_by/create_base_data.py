import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import os.path
from tqdm import tqdm


root = 'https://abw.by/cars'
brands = np.load('../base_data_av_by/brands.npy', allow_pickle=True).item()
brands_abw = np.load('brands.npy', allow_pickle=True).item()


def start_browser():
    res = None
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        #options.add_argument('headless')    # закомментируй, если хочется видеть браузер
        options.add_argument('--verbose')
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        driver.set_page_load_timeout(60)
        res = driver
    except:
        pass
    return res


def get_brands():       # парсим все бренды авто и записывем в файл 'brands.npy'
    driver = start_browser()
    driver.get(root)
    time.sleep(1.5)
    brands_list = {}

    for brand in tqdm(brands):
        brand_show = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div[1]/div[1]/div/div[2]/div/div').click()
        time.sleep(0.1)
        brands_type = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div[1]/div[1]/div/div[2]/div/ul/li[1]/div/div/input').send_keys(brand)
        time.sleep(1)
        try:
            brands_name = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div[1]/div[1]/div/div[2]/div/ul/li[2]').click()
            link = driver.current_url[20:]
        except:
            time.sleep(0.15)
            brands_clear_type = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div[1]/div[1]/div/div[2]/div/ul/li[1]/div/div/input').send_keys(Keys.SHIFT + Keys.HOME + Keys.DELETE)
            link = ''
            time.sleep(0.15)
          # получаем ссылку с ввода в браузер
        brands_list.update({brand: link})
    np.save('brands.npy', brands_list)  # сохраняем все в файл
    print('OK--парсинг брендов')


def get_models():
    try:
        driver = start_browser()
        for brand in tqdm(brands_abw):
            if not os.path.exists(f'models_part_url/{brand}.npy') and brands_abw[brand] != None:
                driver.get(f'{root}/{brands_abw[brand]}')
                time.sleep(2)
                models = np.load(f'../base_data_av_by/models/{brand}.npy', allow_pickle=True).item()    # открываем файл с именем бренда
                models_list = {}
                for model in models:
                    model_show = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div/div[1]/div/div[3]/div/div').click()  # кликаем на модель
                    time.sleep(0.5)
                    model_input = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div/div[1]/div/div[3]/div/ul/li[1]/div/div/input').send_keys(model)  # вводим модель
                    time.sleep(0.5)
                    try:
                        model_input = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div/div[1]/div/div[3]/div/ul/li[2]').click()
                        time.sleep(0.5)
                        link = driver.current_url.split('/')[-1]
                    except:
                        model_show = driver.find_element(By.XPATH,
                                                         '//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div/div[1]/div/div[3]/div/div').click()
                        brands_clear_type = driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/main/div/div[1]/div/div/div[1]/div/div[3]/div/ul/li[1]/div/div/input').send_keys(Keys.SHIFT + Keys.HOME + Keys.DELETE)
                        time.sleep(0.5)
                        link = None
                    models_list.update({model: link})
                np.save(f'models_part_url/{brand}.npy', models_list)
    except:
        return get_models()


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}


def get_from_json_brands():
    url = 'https://b.abw.by/api/adverts/cars/filters'
    r = requests.get(url, headers=headers).json()
    brands = {}
    for car in tqdm(r['filters']['2']['options']):
        id = car['id']
        name = car['title']
        slug = car['slug']
        brands.update({name: [id, f'brand_{slug}']})
    np.save('brands_name_id_slug.npy', brands)


def get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://b.abw.by/api/adverts/cars/filters/'
    brands = np.load('brands_name_id_slug.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][1]}', headers=headers).json()
        models_dict = {}
        for car in r['filters']['3']['options']:
            id = car['id']
            name = car['title']
            slug = car['slug']
            models_dict.update({name: [id, name, f'model_{slug}']})
        brand_dict.update({item: models_dict})
    np.save(f'brands_dict_models.npy', brand_dict)


if __name__ == '__main__':
    pass

