import numpy as np
import requests
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE


def abw_get_from_json_brands():
    url = 'https://b.abw.by/api/adverts/cars/filters'
    r = requests.get(url, headers=HEADERS_JSON).json()
    brands = {}
    price_list = []
    for car in tqdm(r['filters']['2']['options']):
        id = car['id']
        name = car['title']
        slug = car['slug']
        brands.update({name: [id, f'brand_{slug}']})
    np.save(f'{FOLDER_PARSE}abw_brands.npy', brands)
    for price in tqdm(r['filters']['10']['options']):
        price_cost = price['slug']
        price_list.append(price_cost)
    np.save(f'{FOLDER_PARSE}abw_price_list.npy', price_list)


def abw_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://b.abw.by/api/adverts/cars/filters/'
    brands = np.load(f'{FOLDER_PARSE}abw_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][1]}', headers=HEADERS_JSON).json()
        models_dict = {}
        for car in r['filters']['3']['options']:
            id = car['id']
            name = car['title']
            slug = car['slug']
            models_dict.update({name: [id, name, f'model_{slug}']})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}abw_models.npy', brand_dict)