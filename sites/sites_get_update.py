import os

from logic.constant import FOLDER_PARSE

from sites.abw.abw import abw_get_from_json_brands, abw_get_from_json_models
from sites.av.av import av_get_from_json_brands, av_get_from_json_models
from sites.kufar.kufar import kufar_get_from_json_brands, kufar_get_from_json_models
from sites.onliner.onliner import onliner_get_from_json_brands, onliner_get_from_json_models

from sites.sites_fu import create_folders


def parse():
    av_get_from_json_brands()
    av_get_from_json_models()
    abw_get_from_json_brands()
    abw_get_from_json_models()
    onliner_get_from_json_brands()
    onliner_get_from_json_models()
    kufar_get_from_json_brands()
    kufar_get_from_json_models()


def parse_brand_models():
    if not os.path.exists(f'{FOLDER_PARSE}av_brands.npy'):
        create_folders()
    parse()
