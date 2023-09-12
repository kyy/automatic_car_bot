import numpy as np
import requests
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE


def av_get_from_json_brands():
    url = 'https://api.av.by/home/filters/home/init'
    r = requests.get(url, headers=HEADERS_JSON).json()
    brands = {}
    for car in tqdm(r['blocks'][0]['rows'][0]['propertyGroups'][0]['properties'][0]['value'][0][1]['options']):
        id = car['id']
        name = car['label']
        rr = requests.get('https://api.av.by/offer-types/cars/landings/', HEADERS_JSON).json()
        for ids in rr['seo']['links']:
            if ids['label'] == name:
                slug = ids['url'].split('/')[-1]
            brands.update({name: [id, slug]})
    np.save(f'{FOLDER_PARSE}av_brands.npy', brands)


def av_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://api.av.by/offer-types/cars/landings/'
    brands = np.load(f'{FOLDER_PARSE}av_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][1]}', headers=HEADERS_JSON).json()
        models_dict = {}
        for car in r['seo']['links']:
            name = car['label']
            slug = car['url'].split('/')[-1]
            try:
                rr = requests.get(f'{url}{brands[item][1]}/{slug}', headers=HEADERS_JSON).json()
                id = rr['metadata']['modelId']
            except:
                continue
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}av_models.npy', brand_dict)
