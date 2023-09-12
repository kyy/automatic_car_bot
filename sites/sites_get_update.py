import os
import aiohttp

from logic.constant import FOLDER_PARSE

from sites.av.av import get_av_brands_models
from sites.abw.abw import get_abw_brands_models
from sites.sites_fu import create_folders


async def get_parse_brands_models():
    if not os.path.exists(f'{FOLDER_PARSE}av_brands.npy'):
        create_folders()

    async with aiohttp.ClientSession() as session:
        await get_av_brands_models(session)
        await get_abw_brands_models(session)
