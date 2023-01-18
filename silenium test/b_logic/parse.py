import requests
from bs4 import BeautifulSoup
import numpy as np
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

# необходимо логинится
def clicking(driver):
    try:
        click_show_phone = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[2]/div[3]/div[2]/div[2]/div[5]/button[2]').click()
        time.sleep(0.3)
        click_show_vin = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div[1]/div[2]/div[3]/div[6]/div[1]/button/span/small').click()
        time.sleep(0.3)
    except: pass


def parse_av_by(filter_link):
    start = time.time()
    driver = start_browser()
    driver.get(filter_link)
    marka_link = driver.find_elements(By.CLASS_NAME, 'listing-item__wrap')
    full = []
    try:
        i = 0
        for items in tqdm(marka_link):
            i += 1
            link = items.find_element(By.CSS_SELECTOR, 'a.listing-item__link').get_attribute('href')
            model = items.find_element(By.CSS_SELECTOR, 'span.link-text').text
            city = items.find_element(By.CSS_SELECTOR, 'div.listing-item__location').text
            data = items.find_element(By.CSS_SELECTOR, 'div.listing-item__date').text
            cost = items.find_element(By.CSS_SELECTOR, 'div.listing-item__priceusd').text.replace('\u2009', '').replace('≈ ', '')
            info = items.find_element(By.CSS_SELECTOR, 'div.listing-item__params').text.replace('\u2009', '').replace('\n', ' ')
            full.append([i, model, cost, info, 'vin number', data, city, 'phone'])


        print('OK--av.by')
    except Exception as e:
        print('ERROR--av.by', e)
    end = time.time() - start
    print(f'Итоговое время парсинга: {end}')
    np.save(f'parse_av_by.npy', full)
    return full


link = 'https://cars.av.by/filter?brands[0][brand]=8&brands[0][model]=5867&year[min]=2015&year[max]=2022&price_usd[min]=1&price_usd[max]=100000&transmission_type=1'
if __name__ == '__main__':
    parse_av_by(link)
