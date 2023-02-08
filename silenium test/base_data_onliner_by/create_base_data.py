import numpy as np
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
import time
from webdriver_manager.chrome import ChromeDriverManager
import os.path
from tqdm import tqdm


root = 'https://ab.onliner.by/'
brands = np.load('../base_data_av_by/brands.npy', allow_pickle=True).item()
brands_av = np.load('brands.npy', allow_pickle=True).item()


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
    driver.maximize_window()
    time.sleep(1.5)
    brands_list = {}
    for brand in brands:
        driver.find_element(
            By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div[2]/div[2]'
                      '/div/div[2]/div[1]/div/div/div[1]/div').click()
        time.sleep(0.15)
        driver.find_element(
            By.XPATH, '/html/body/div[1]/div/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div[2]/div[2]/'
                      'div/div[2]/div[1]/div/div/div[1]/div/div[2]/div[1]/div/input').send_keys(brand)
        time.sleep(0.15)
        try:
            driver.find_element(
                By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div[2]/'
                          'div[2]/div/div[2]/div[1]/div/div/div[1]/div/div[2]/div[2]/div/div[3]/ul/li/label/div/'
                          'div[2]').click()
            time.sleep(1.1)
            print(driver.current_url)
            link = driver.current_url[22:]
        except:
            time.sleep(0.15)
            driver.find_element(
                By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]/div[2]/'
                          'div[2]/div/div[2]/div[1]/div/div/div[1]/div/div[2]/div[1]/div/input')\
                .send_keys(Keys.SHIFT + Keys.HOME + Keys.DELETE)
            link = None
            time.sleep(0.15)
        print(brand, link)
        brands_list.update({brand: link})
    np.save('brands.npy', brands_list)
    print('OK--парсинг брендов')


def correction_brand():
    brands = np.load('brands.npy', allow_pickle=True).item()
    brands['Plymouth'] = 'plymouth'
    brands['Lada (ВАЗ)'] = 'lada'
    brands['Porsche'] = 'porsche'
    brands['Land Rover'] = 'land-rover'
    brands['Cadillac'] = 'cadillac'
    brands['Datsun'] = 'datsun'
    brands['GAC'] = None
    np.save('brands.npy', brands)


def get_models():
    try:
        driver = start_browser()
        driver.maximize_window()
        for brand in tqdm(brands_av):
            if not os.path.exists(f'models_part_url/{brand}.npy') and brands_av[brand] != None:
                driver.get(f'{root}{brands_av[brand]}')
                time.sleep(2)
                models = np.load(f'../base_data_av_by/models/{brand}.npy', allow_pickle=True).item()
                models_list = {}
                for model in models:
                    driver.find_element(
                        By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]/'
                                  'div[2]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div[2]').click()

                    driver.find_element(
                        By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]/'
                                  'div[2]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div/'
                                  'input').send_keys(model)
                    time.sleep(0.1)
                    try:
                        driver.find_element(
                            By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/'
                                      'div[2]/div[2]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[2]/div/'
                                      'div[2]/ul/li/label/div/div[2]/div').click()
                        time.sleep(2)
                        link = driver.current_url.split('/')[-1]
                    except:
                        driver.find_element(
                            By.XPATH, '//*[@id="container"]/div/div/div/div/div/div[2]/div/div/div[3]/div/div[2]/div[2]'
                                      '/div[2]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[2]/div[1]/div/'
                                      'input').send_keys(Keys.SHIFT + Keys.HOME + Keys.DELETE)
                        time.sleep(0.1)
                        link = None
                    models_list.update({model: link})
                print(brand, models_list)
                np.save(f'models_part_url/{brand}.npy', models_list)
    except:
        #return get_models()
        print('errno')


if __name__ == '__main__':
    pass


