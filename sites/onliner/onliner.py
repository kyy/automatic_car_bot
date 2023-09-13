import logging

import numpy as np
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE


async def onliner_get_from_json_brands(session):
    brands = {}
    async with session.get(
            url='https://ab.onliner.by/sdapi/ab.api/dictionaries',
            headers=HEADERS_JSON,
    ) as resp:
        r = await resp.json(content_type=None)
        for car in tqdm(r['manufacturer']):
            id = car['id']
            name = car['name']
            slug = car['slug']
            brands.update({name: [id, slug]})
    np.save(f'{FOLDER_PARSE}onliner_brands.npy', brands)


async def onliner_get_from_json_models(session):  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://ab.onliner.by/sdapi/ab.api/manufacturers/'
    brands = np.load(f'{FOLDER_PARSE}onliner_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        async with session.get(
                url=f'{url}{brands[item][0]}',
                headers=HEADERS_JSON,
        ) as resp:
            models_dict = {}
            r = await resp.json(content_type=None)
            for car in r['models']:
                id = car['id']
                name = car['name']
                slug = car['slug']
                models_dict.update({name: [id, name, slug]})
            brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}onliner_models.npy', brand_dict)


async def get_onliner_brands_models(session):
    try:
        logging.info('start onliner <- brands parsing...')
        await onliner_get_from_json_brands(session)
    except Exception as e:
        logging.error(f'<onliner.onliner_get_from_json_brands> {e}')
    try:
        logging.info('start onliner <- models parsing...')
        await onliner_get_from_json_models(session)
    except Exception as e:
        logging.error(f'<onliner.onliner_get_from_json_models> {e}')
