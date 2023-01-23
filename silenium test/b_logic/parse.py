import numpy as np
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from .static.passw import AV_BY


def start_browser():
    res = None
    try:
        options = webdriver.ChromeOptions()
        #options = webdriver.FirefoxOptions()
        options.add_argument("--no-sandbox")
        options.add_argument('--headless')  # закомментируй, если хочется видеть браузер
        options.add_argument('--verbose')
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        #driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
        driver.set_page_load_timeout(60)
        res = driver
    except:
        pass
    return res


def click_cookies(driver):
    try:
        click_cookies = driver.find_element(By.XPATH, '//*[@id="__next"]/div[3]/div/div/button').click()
    except:
        pass


def login(driver):
    driver.get('https://av.by/login')
    time.sleep(0.5)
    login = driver.find_element(By.CSS_SELECTOR, '#phone')
    time.sleep(0.5)
    login.click()
    time.sleep(0.5)
    login.send_keys(AV_BY[0])
    password = driver.find_element(By.CSS_SELECTOR, 'div.tabcontent:nth-child(1) > div:nth-child(1) > form:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > input:nth-child(1)').send_keys(AV_BY[1])
    time.sleep(0.5)
    enter = driver.find_element(By.XPATH, '//*[@id="__next"]/div[2]/main/div/div/div/div/div[1]/div/div[2]/div/div[1]/div/form/div/div[4]/button').click()


def car_cards_parse(driver, filter_link):
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
            cost = items.find_element(By.CSS_SELECTOR, 'div.listing-item__priceusd').text.replace('\u2009', '').replace(
                '≈ ', '')
            info = items.find_element(By.CSS_SELECTOR, 'div.listing-item__params').text.replace('\u2009', '').replace(
                '\n', ' ')
            full.append([link, 'комментарий', i, 'обмен', model, cost, info, data, city, 'имя', 'телефон'])
        print('OK--av.by--main--page')
    except Exception as e:
        print('ERROR--av.by--main--page', e)
    return full


def retry(driver, url,  n=3, t=0):
    while t < n:
        try:
            driver.get(url)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card__comment-text")))
            time.sleep(1)
            return True
        except:
            t += 1
            print(f'{t} - попытка подключения к {url}')
            time.sleep(1)
            driver.refresh()
            return retry


def from_card_parse(driver, full):
    for i in tqdm(range(len(full))):
        url = full[i][0]
        if retry(driver, url, 3) is True:
            try:
                show_phone_number = driver.find_element(By.CSS_SELECTOR, 'button.button--secondary:nth-child(2)')
                driver.execute_script("arguments[0].scrollIntoView();", show_phone_number)
                time.sleep(0.3)
                show_phone_number.click()
            except:
                show_phone_number2 = driver.find_element(By.CSS_SELECTOR, '.card__contact > button:nth-child(1)')
                driver.execute_script("arguments[0].scrollIntoView();", show_phone_number2)
                time.sleep(0.3)
                show_phone_number2.click()
            time.sleep(0.3)
            try:
                full[i][10] = driver.find_element(By.CSS_SELECTOR, '.phones__list > li:nth-child(1)').text
            except:
                full[i][10] = ''
                print('не удалось получить телефон')
            time.sleep(0.15)
            try:
                full[i][9] = driver.find_element(By.CSS_SELECTOR, '.phones__owner').text[0:35].title()
            except:
                full[i][9] = ''
                print('не удалось получить имя')
            time.sleep(0.15)
            try:
                full[i][1] = ''
                comments = driver.find_elements(By.CLASS_NAME, 'card__comment-text')
                for it in comments:
                    full[i][1] += it.find_element(By.TAG_NAME, 'p').text
            except:
                full[i][1] = ''
                print('не удалось получить комментарий')
            time.sleep(0.15)
            try:
                full[i][3] = driver.find_element(By.CLASS_NAME, 'card__exchange-title').text.replace('/', '+').replace('\u2022', '-')
            except:
                full[i][3] = ''
                print('не удалось получить информацию об обмене')
    return full


def parse_av_by(filter_link):
    start = time.time()
    driver = start_browser()
    driver.maximize_window()
    click_cookies(driver)
    full = car_cards_parse(driver, filter_link)
    full_name_phone = from_card_parse(driver, full)
    np.save(f'parse_av_by.npy', full_name_phone)
    end = time.time() - start
    print(f'Время парсинга: {end}')
    return full_name_phone


if __name__ == '__main__':
    pass

