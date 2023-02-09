import numpy as np
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os.path
from tqdm import tqdm


root = 'https://abw.by/cars'
brands = np.load('../base_data_av_by/brands.npy', allow_pickle=True).item()
brands_abw = np.load('brands.npy', allow_pickle=True).item()
print(brands_abw)


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
        for brand in brands_abw:
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
                print(brand, models_list)
                np.save(f'models_part_url/{brand}.npy', models_list)

    except:
        return get_models()


if __name__ == '__main__':
    get_models()
