import asyncio

import pytest

from .cook_parse_cars import parse_main as parse_cars
from .cook_parse_prices import parse_main as parse_prices
from work import send_car_job


@pytest.fixture
def json_value():

    return dict(
        av_json='https://api.av.by/offer-types/cars/filters/main/init?brands[0][brand]=43&year[min]=2000&year[max]=2023&price_usd[min]=500&price_usd[max]=100000&engine_capacity[min]=1000&engine_capacity[max]=9000&&sort=4]',
        abw_json='https://b.abw.by/api/adverts/cars/list/brand_citroen/engine_benzin,dizel,gibrid,sug/transmission_at,mt/year_2000:2023/price_500:100000/volume_1000:9000/?sort=new',
        onliner_json='https://ab.onliner.by/sdapi/ab.api/search/vehicles?car[0][manufacturer]=2&year[from]=2000&year[to]=2023&price[from]=500&price[to]=100000&engine_capacity[from]=1.0&engine_capacity[to]=9.0&order=created_at:desc&price[currency]=USD]',
        kufar_json='https://api.kufar.by/search-api/v1/search/rendered-paginated?cat=2010&sort=lst.d&typ=sell&lang=ru&cur=USD&size=50&cbnd2=category_2010.mark_citroen&rgd=r:2000,2023&prc=r:500,100000&crca=r:1,230',
    )


def test_parse_cars():

    result = asyncio.ensure_future(parse_cars(
        json=json_value,
        name='test_parse_cars',
        work=False,
        send_car_job=None,
        tel_id=514390056,
    ))
    assert result


def test_parse_cars_true():

    result = asyncio.ensure_future(parse_cars(
        json=json_value,
        name='test_parse_cars_true',
        work=True,
        send_car_job=send_car_job,
        tel_id=514390056,
    ))
    assert result


def test_parse_prices():

    result = asyncio.ensure_future(parse_prices(ctx=None))
    assert result
