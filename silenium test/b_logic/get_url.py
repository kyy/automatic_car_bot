from .constant_fu import s_s, s_b
#from constant_fu import s_s, s_b
import asyncio
import aiosqlite

# av.by
async def get_url_av(car_input, db):
    """
    Формируем гет запрос для av.by
    :param car_input: filter_short
    :return: гет запрос
    """

    # Входные параметры
    param_input = ['brands[0][brand]=', 'brands[0][model]=', 'engine_type[0]=', 'transmission_type=', 'year[min]=',
                   'year[max]=', 'price_usd[min]=', 'price_usd[max]=', 'engine_capacity[min]=', 'engine_capacity[max]=']

    # База данных
    car_input = dict(zip(param_input, car_input.split(s_s)))
    transmission = {'a': '1', 'm': '2'}
    motor = {'b': '1', 'bpb': '2', 'bm': '3', 'bg': '4', 'd': '5', 'dg': '6', 'e': '7'}
    brand = car_input['brands[0][brand]=']
    model = car_input['brands[0][model]=']
    if model != s_b:
        cursor = await db.execute(f"select brands.av_by, models.av_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'")
        rows = await cursor.fetchall()
        car_input['brands[0][brand]='] = rows[0][0]
        car_input['brands[0][model]='] = rows[0][1]
    else:
        cursor = await db.execute(f"select brands.av_by, models.av_by  from brands "
                                  f"inner join models on brands.id = models.brand_id "
                                  f"where brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        car_input['brands[0][model]='] = s_b
        car_input['brands[0][brand]='] = rows[0][0]


    if car_input['engine_type[0]='] in motor:
        car_input['engine_type[0]='] = motor[car_input['engine_type[0]=']]
    if car_input['transmission_type='] in transmission:
        car_input['transmission_type='] = transmission[car_input['transmission_type=']]

    new_part = []
    for key in car_input:
        if car_input[key] != s_b:
            new_part.append(str(key)+str(car_input[key]))
    new_part_url = '&'.join(new_part)
    full_url = f'https://cars.av.by/filter?{new_part_url}'
    return full_url


# abw.by
def get_url_abw(car_input):
    """
    Формируем гет запрос для abw.by
    :param car_input: filter_short
    :return: гет запрос
    """
    pass

link = 'BMW+X5+b+a+?+?+?+?+?+?'
async def all_get_url(link):
    async with aiosqlite.connect('./auto_db') as db:
        return asyncio.run(get_url_av(link, db))


if __name__ == '__main__':
    #asyncio.run(all_get_url())
    pass
