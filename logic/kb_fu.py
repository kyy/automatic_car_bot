from functools import lru_cache

import numpy as np
from aiocache import cached, Cache

from logic.constant import MM
from logic.database.config import database
from logic.text import TXT


def pagination(data: iter, name: str, ikb, per_page=3, cur_page=1):
    """
    Разбиваем итерируемую последовательность на страницы
    :param data: our data
    :param name: cb_name indention
    :param cur_page: number of current page from callback
    :param per_page: number of items per page
    :param ikb: InlineKeyboardButton
    :return: data, buttons ([<<], [1/23], [>>]), del_pages (callback for correctly deleting)
    Handler example:
            @router.callback_query((F.data.endswith('{:param name}_prev')) | (F.data.endswith('{:param name}_next')))
            async def pagination_params(callback: CallbackQuery):
            async with database() as db:
                page = int(callback.data.split('_')[0])
                await callback.message.edit_text(
                    'keyboard',
                    reply_markup=await params_menu_kb(:param cur_page))
    """
    lsp = len(data)
    pages = (lsp // per_page + 1) if (lsp % per_page != 0) else (lsp // per_page)
    cb_next = 2
    cb_prev = pages
    buttons = []
    if lsp > per_page:
        if cur_page == 1:
            data = data[0:per_page]
        elif pages == cur_page:
            data = data[cur_page * per_page - per_page:]
            cb_next = 1
            cb_prev = pages - 1
        elif pages > cur_page > 1:
            data = data[cur_page * per_page - per_page:cur_page * per_page]
            cb_next = cur_page + 1
            cb_prev = cur_page - 1
        buttons = [ikb(text=TXT['btn_page_left'], callback_data=f'{cb_prev}_{name}_prev'),
                   ikb(text=f'{cur_page}/{pages}', callback_data=f'1_{name}_prev'),
                   ikb(text=TXT['btn_page_right'], callback_data=f'{cb_next}_{name}_next')]
    del_page = cur_page
    if cur_page == pages:
        del_page = pages - 1 if (lsp % per_page == 1) and cur_page > 1 else cur_page
    return data, buttons, del_page


@cached(ttl=300, cache=Cache.MEMORY, key='brands', namespace="get_brands")
async def get_brands() -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT [unique] FROM brands ORDER BY [unique]")
        rows = await cursor.fetchall()
        brands = []
        for brand in rows:
            brands.append(brand[0])
    return brands


@cached(ttl=300, cache=Cache.MEMORY, namespace="get_models")
async def get_models(brand: str) -> list[str]:
    async with database() as db:
        cursor = await db.execute(f"SELECT models.[unique] FROM models "
                                  f"INNER JOIN brands on brands.id =  models.brand_id "
                                  f"WHERE brands.[unique] = '{brand}'")
        rows = await cursor.fetchall()
        models = []
        for brand in rows:
            models.append(brand[0])
    return models


@lru_cache()
def get_years(
        from_year: int = MM['MIN_YEAR'],
        to_year=MM['MAX_YEAR']
) -> list[str]:
    return [str(i) for i in range(from_year, to_year + 1)]


@lru_cache()
def get_dimension(
        from_dim: float = MM['MIN_DIM'],
        to_dim: float = MM['MAX_DIM'] + 0.1,
        step: float = MM['STEP_DIM']
) -> list[str]:
    return [str(round(i, 1)) for i in np.arange(from_dim, to_dim, step)]


@lru_cache()
def get_cost(
        from_cost: int = MM['MIN_COST'],
        to_cost: int = MM['MAX_COST'] + MM['STEP_COST'],
        step: int = MM['STEP_COST']
) -> list[str]:
    return [str(i) for i in range(from_cost, to_cost, step)]
