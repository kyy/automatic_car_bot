import logging

import numpy as np
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE


async def kufar_get_from_json_brands(session):
    brands = {}
    async with session.get(
            url='https://api.kufar.by/catalog/v1/nodes?tag=category_2010&view=taxonomy',
            headers=HEADERS_JSON,
    ) as resp:
        r = await resp.json(content_type=None)
        for car in tqdm(r):
            id = car['value']
            name = car['labels']['ru']
            slug = id.split('mark_')[1].replace('_', '-')
            brands.update({name: [id, slug]})
    np.save(f'{FOLDER_PARSE}kufar_brands.npy', brands)


async def kufar_get_from_json_models(session):  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://api.kufar.by/catalog/v1/nodes?tag={model}&view=taxonomy'
    brands = np.load(f'{FOLDER_PARSE}kufar_brands.npy', allow_pickle=True).item()
    brand_dict = {}
    for item in tqdm(brands):
        async with session.get(
                url=url.format(model=brands[item][0]),
                headers=HEADERS_JSON
        ) as resp:
            r = await resp.json(content_type=None)
            models_dict = {}
            for car in r:
                name = car['labels']['ru']
                id = car['value']
                slug = id.split('mark_')[1].replace('_', '-').replace('.', '-')
                models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}kufar_models.npy', brand_dict)


async def get_kufar_brands_models(session):
    try:
        logging.info('start kufar <- brands parsing...')
        await kufar_get_from_json_brands(session)
    except Exception as e:
        logging.error(f'<kufar.kufar_get_from_json_brands> {e}')
    try:
        logging.info('start kufar <- models parsing...')
        await kufar_get_from_json_models(session)
    except Exception as e:
        logging.error(f'<kufar.kufar_get_from_json_models> {e}')
