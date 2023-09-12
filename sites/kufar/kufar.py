import numpy as np
import requests
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE


def kufar_get_from_json_brands():
    url = 'https://api.kufar.by/catalog/v1/nodes?tag=category_2010&view=taxonomy'
    r = requests.get(url, headers=HEADERS_JSON).json()
    brands = {}
    for car in tqdm(r):
        id = car['value']
        name = car['labels']['ru']
        slug = id.split('mark_')[1].replace('_', '-')
        brands.update({name: [id, slug]})
    np.save(f'{FOLDER_PARSE}kufar_brands.npy', brands)


def kufar_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://api.kufar.by/catalog/v1/nodes?tag={model}&view=taxonomy'
    brands = np.load(f'{FOLDER_PARSE}kufar_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(url.format(model=brands[item][0]), headers=HEADERS_JSON).json()
        models_dict = {}
        for car in r:
            name = car['labels']['ru']
            id = car['value']
            slug = id.split('mark_')[1].replace('_', '-').replace('.', '-')
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}kufar_models.npy', brand_dict)
