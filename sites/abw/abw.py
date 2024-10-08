import logging

import numpy as np
from tqdm import tqdm

from logic.constant import HEADERS, FOLDER_PARSE


async def abw_get_from_json_brands(session):
    brands, price_list = {}, []
    async with session.get(
            url='https://b.abw.by/api/adverts/cars/filters',
            headers=HEADERS,
    ) as resp:
        r = await resp.json(content_type=None)

        for i in range(len(r['filters'])):
            r_t = r['filters'][i]
            if r_t['id'] == 'brand':
                brand_index = i
            elif r_t['id'] == 'price':
                price_index = i

        for car in tqdm(r['filters'][brand_index]['options']):
            id = car['id']
            name = car['title']
            slug = car['slug']
            brands.update({name: [id, f'brand_{slug}']})
        np.save(f'{FOLDER_PARSE}abw_brands.npy', brands)
        logging.info('start abw <- price list parsing...')

        for price in tqdm(r['filters'][price_index]['options']):
            price_cost = price['slug']
            price_list.append(price_cost)
    np.save(f'{FOLDER_PARSE}abw_price_list.npy', price_list)


async def abw_get_from_json_models(session):  # {Brand_name:{Model_name:[id, name, slug]}}
    url = 'https://b.abw.by/api/adverts/cars/filters/'
    brand_dict = {}
    brands = np.load(f'{FOLDER_PARSE}abw_brands.npy', allow_pickle=True).item()

    for item in tqdm(brands):
        async with session.get(
                url=f'{url}{brands[item][1]}',
                headers=HEADERS,
        ) as resp:
            models_dict = {}
            r = await resp.json(content_type=None)

            for i in range(len(r['filters'])):
                r_t = r['filters'][i]
                if r_t['id'] == 'model':
                    model_index = i

            for car in r['filters'][model_index]['options']:
                id = car['id']
                name = car['title']
                slug = car['slug']
                models_dict.update({name: [id, name, f'model_{slug}']})
        brand_dict.update({item: models_dict})
    np.save(f'{FOLDER_PARSE}abw_models.npy', brand_dict)


async def get_abw_brands_models(session):
    try:
        logging.info('start abw <- brands parsing...')
        await abw_get_from_json_brands(session)
    except Exception as e:
        logging.error(f'<abw.abw_get_from_json_brands> {e}')
    try:
        logging.info('start abw <- models parsing...')
        await abw_get_from_json_models(session)
    except Exception as e:
        logging.error(f'<abw.abw_get_from_json_models> {e}')
