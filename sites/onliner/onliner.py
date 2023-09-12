import numpy as np
import requests
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE


def onliner_get_from_json_brands():
    url = 'https://ab.onliner.by/sdapi/ab.api/dictionaries'
    r = requests.get(url, headers=HEADERS_JSON).json()
    brands = {}
    for car in tqdm(r['manufacturer']):
        id = car['id']
        name = car['name']
        slug = car['slug']
        brands.update({name: [id, slug]})
    np.save(f'{FOLDER_PARSE}onliner_brands.npy', brands)


def onliner_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://ab.onliner.by/sdapi/ab.api/manufacturers/'
    brands = np.load(f'{FOLDER_PARSE}onliner_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][0]}', headers=HEADERS_JSON).json()
        models_dict = {}
        for car in r['models']:
            id = car['id']
            name = car['name']
            slug = car['slug']
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}onliner_models.npy', brand_dict)