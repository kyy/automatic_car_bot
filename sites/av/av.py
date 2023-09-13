import logging

import numpy as np
from tqdm import tqdm

from logic.constant import HEADERS_JSON, FOLDER_PARSE
from aiologger.loggers.json import JsonLogger


logger = JsonLogger.with_default_handlers(serializer_kwargs={'ensure_ascii': False})


async def av_get_from_json_brands(session):
    brands = {}
    async with session.get(
            url='https://api.av.by/home/filters/home/init',
            headers=HEADERS_JSON
    ) as resp:
        r = await resp.json(content_type=None)
        for car in tqdm(r['blocks'][0]['rows'][0]['propertyGroups'][0]['properties'][0]['value'][0][1]['options']):
            id = car['id']
            name = car['label']
            async with session.get(
                    url='https://api.av.by/offer-types/cars/landings/',
                    headers=HEADERS_JSON
            ) as resp2:
                r2 = await resp2.json(content_type=None)
                for ids in r2['seo']['links']:
                    if ids['label'] == name:
                        slug = ids['url'].split('/')[-1]
                    brands.update({name: [id, slug]})
    np.save(f'{FOLDER_PARSE}av_brands.npy', brands)


async def av_get_from_json_models(session):  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://api.av.by/offer-types/cars/landings/'
    brand_dict = {}
    brands = np.load(f'{FOLDER_PARSE}av_brands.npy', allow_pickle=True).item()
    for item in tqdm(brands):
        async with session.get(
                url=f'{url}{brands[item][1]}',
                headers=HEADERS_JSON,
        ) as resp:
            models_dict = {}
            r = await resp.json(content_type=None)
            for car in r['seo']['links']:
                name = car['label']
                slug = car['url'].split('/')[-1]
                try:
                    async with session.get(
                            url=f'{url}{brands[item][1]}/{slug}',
                            headers=HEADERS_JSON
                    ) as resp2:
                        r2 = await resp2.json(content_type=None)
                        id = r2['metadata']['modelId']
                except Exception as e:
                    logging.error(f'<av.av_get_from_json_models> {e}')
                    continue
                models_dict.update({name: [id, name, slug]})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}av_models.npy', brand_dict)


async def get_av_brands_models(session):
    try:
        logging.info('start av <- brands parsing...')
        await av_get_from_json_brands(session)
    except Exception as e:
        logging.error(f'<av.av_get_from_json_brands> {e}')
    try:
        logging.info('start av <- models parsing...')
        await av_get_from_json_models(session)
    except Exception as e:
        logging.error(f'<av.av_get_from_json_brands> {e}')
