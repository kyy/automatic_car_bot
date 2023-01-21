import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from tqdm import tqdm
from .static.passw import AV_BY



def start_browser():
    res = None
    try:
        #options = webdriver.ChromeOptions()
        options = webdriver.FirefoxOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('headless')  # закомментируй, если хочется видеть браузер
        options.add_argument('--verbose')
        options.add_argument("--disable-dev-shm-usage")
        #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        driver.set_page_load_timeout(60)
        res = driver
    except:
        pass
    return res

def login(driver):
    driver.get('https://av.by/login')
    try:
        click_cookies = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div/button').click()
    except:
        pass
    time.sleep(1)
    login = driver.find_element(By.CSS_SELECTOR, '#phone')
    time.sleep(1)
    login.click()
    time.sleep(1)
    login.send_keys(AV_BY[0])
    password = driver.find_element(By.CSS_SELECTOR, 'div.tabcontent:nth-child(1) > div:nth-child(1) > form:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > input:nth-child(1)').send_keys(AV_BY[1])
    time.sleep(1)
    enter = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div/div/div[1]/div/div[2]/div/div[1]/div/form/div/div[4]/button').click()


def parse_av_by(filter_link):
    start = time.time()
    driver = start_browser()
    driver.maximize_window()
    login(driver)
    driver.get(filter_link)
    marka_link = driver.find_elements(By.CLASS_NAME, 'listing-item__wrap')
    full = []
    try:
        i = 0
        for items in tqdm(marka_link):
            i += 1
            model = items.find_element(By.CSS_SELECTOR, 'span.link-text').text
            link = items.find_element(By.CSS_SELECTOR, 'a.listing-item__link').get_attribute('href')
            city = items.find_element(By.CSS_SELECTOR, 'div.listing-item__location').text
            data = items.find_element(By.CSS_SELECTOR, 'div.listing-item__date').text
            cost = items.find_element(By.CSS_SELECTOR, 'div.listing-item__priceusd').text.replace('\u2009', '').replace('≈ ', '')
            info = items.find_element(By.CSS_SELECTOR, 'div.listing-item__params').text.replace('\u2009', '').replace('\n', ' ')
            full.append([link, i, model, cost, info, 'vin number', data, city, 'phone'])
        print('OK--av.by--main--page')
    except Exception as e:
        print('ERROR--av.by--main--page', e)
    try:
        for i in tqdm(range(len(full))):
            url = full[i][0]
            driver.get(url)
            time.sleep(2)
            vin_hidden = driver.find_element(By.CSS_SELECTOR, 'button.card__vin-button')
            try:
                driver.execute_script("arguments[0].scrollIntoView();", vin_hidden)
                vin_hidden.click()
            except:
                pass
            time.sleep(0.1)
            try:
                full[i][5] = driver.find_element(By.CSS_SELECTOR, 'div.card__vin-number').text
            except:
                full[i][5] = 'None'
    except Exception as e:
        print('ERROR--av.by--cards--of--cars', e)
    end = time.time() - start
    print(f'Итоговое время парсинга: {end}')
    np.save(f'parse_av_by.npy', full)
    return full


link = 'https://cars.av.by/ferrari'
if __name__ == '__main__':
    parse_av_by(link)

