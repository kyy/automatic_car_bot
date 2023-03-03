import numpy as np
import requests
from tqdm import tqdm


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/109.0.0.0 Safari/537.36',
        'accept': '*/*',
        'content-type': 'application/json'}


def checking_new_brands_av():
    print('проверка брендов')
    url = 'https://api.av.by/home/filters/home/init'
    brands = np.load('parse/av_brands.npy', allow_pickle=True).item()
    r = requests.get(url, headers=headers).json()
    n_brands_inet = len(r['blocks'][0]['rows'][0]['propertyGroups'][0]['properties'][0]['value'][0][1]['options'])
    try:
        n_brands_stor = len(brands)
    except:
        n_brands_stor = 0
    print(n_brands_stor, n_brands_inet)
    if n_brands_inet != n_brands_stor:
        return False
    else:
        return True


def checking_new_models_av(lenn):
    print('проверка моделей')
    url = 'https://api.av.by/offer-types/cars/landings/'
    brands = np.load('parse/av_brands.npy', allow_pickle=True).item()
    models = np.load('parse/av_models.npy', allow_pickle=True).item()
    n_models_inet = 0
    n_models_stor = lenn(models)
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][1]}', headers=headers).json()
        n_models_inet += len(r['seo']['links'])
    print(n_models_stor, n_models_inet)
    if n_models_inet != n_models_stor:
        return False
    else:
        return True


def av_get_from_json_brands():
    url = 'https://api.av.by/home/filters/home/init'
    r = requests.get(url, headers=headers).json()
    brands = {}
    for car in tqdm(r['blocks'][0]['rows'][0]['propertyGroups'][0]['properties'][0]['value'][0][1]['options']):
        id = car['id']
        name = car['label']
        rr = requests.get('https://api.av.by/offer-types/cars/landings/', headers).json()
        for ids in rr['seo']['links']:
            if ids['label'] == name:
                slug = ids['url'].split('/')[-1]
            brands.update({name: [id, slug]})
    np.save('parse/av_brands.npy', brands)


def av_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://api.av.by/offer-types/cars/landings/'
    brands = np.load('parse/av_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][1]}', headers=headers).json()
        models_dict = {}
        for car in r['seo']['links']:
            name = car['label']
            slug = car['url'].split('/')[-1]
            try:
                rr = requests.get(f'{url}{brands[item][1]}/{slug}', headers=headers).json()
                id = rr['metadata']['modelId']
            except:
                continue
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'parse/av_models.npy', brand_dict)


def abw_get_from_json_brands():
    url = 'https://b.abw.by/api/adverts/cars/filters'
    r = requests.get(url, headers=headers).json()
    brands = {}
    for car in tqdm(r['filters']['2']['options']):
        id = car['id']
        name = car['title']
        slug = car['slug']
        brands.update({name: [id, f'brand_{slug}']})
    np.save('parse/abw_brands.npy', brands)


def abw_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://b.abw.by/api/adverts/cars/filters/'
    brands = np.load('parse/abw_brands.npy', allow_pickle=True).item()
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
    np.save(f'parse/abw_models.npy', brand_dict)


def onliner_get_from_json_brands():
    url = 'https://ab.onliner.by/sdapi/ab.api/dictionaries'
    r = requests.get(url, headers=headers).json()
    brands = {}
    for car in tqdm(r['manufacturer']):
        id = car['id']
        name = car['name']
        slug = car['slug']
        brands.update({name: [id, slug]})
    np.save('parse/onliner_brands.npy', brands)


def onliner_get_from_json_models():  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://ab.onliner.by/sdapi/ab.api/manufacturers/'
    brands = np.load('parse/onliner_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        r = requests.get(f'{url}{brands[item][0]}', headers=headers).json()
        models_dict = {}
        for car in r['models']:
            id = car['id']
            name = car['name']
            slug = car['slug']
            models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save('parse/onliner_models.npy', brand_dict)


def main_parse(lenn):
    if not all([checking_new_brands_av(), checking_new_models_av(lenn)]):
        print('Начинаем обновления')
        av_get_from_json_brands()
        av_get_from_json_models()
        abw_get_from_json_brands()
        abw_get_from_json_models()
        onliner_get_from_json_brands()
        onliner_get_from_json_models()
        return True
    else:
        print('Обновления не требуются')
        return False
