import logging

from logic.constant import FSB, REPORT_PARSE_LIMIT_PAGES, PARSE_LIMIT_PAGES, ROOT_URL
from logic.decorators import timed_lru_cache
from sites.sites_fu import max_min_params


@timed_lru_cache(300)
async def get_url_kufar(car_input, db, work):
    car_input = max_min_params(car_input)
    param_input = ["cbnd2=", "cmdl2=", "cre=", "crg=", "rgd=r:", "rgd_max", "prc=r:", "prc_max", "crca=r:", "crca_max"]
    car_input = dict(zip(param_input, car_input))
    transmission = dict(a="1", m="2")
    motor = dict(b="v.or:1", bpb="v.or:3", bm="v.or:6", bg="v.or:4", d="v.or:2", dg="v.or:7", e="v.or:5")
    brand = car_input["cbnd2="]
    model = car_input["cmdl2="]
    if model != FSB:
        cursor = await db.execute(
            f"select brands.kufar_by, models.kufar_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}' and models.[unique] = '{model}'"
        )
        rows = await cursor.fetchall()
        car_input["cbnd2="] = rows[0][0]
        car_input["cmdl2="] = rows[0][1]
    else:
        cursor = await db.execute(
            f"select brands.kufar_by, models.kufar_by  from brands "
            f"inner join models on brands.id = models.brand_id "
            f"where brands.[unique] = '{brand}'"
        )
        rows = await cursor.fetchall()
        car_input["cmdl2="] = FSB
        car_input["cbnd2="] = rows[0][0]

    if car_input["cre="] in motor:
        car_input["cre="] = motor[car_input["cre="]]
    if car_input["crg="] in transmission:
        car_input["crg="] = transmission[car_input["crg="]]

    dim_k = [i for i in range(1000, 4100, 100)]
    dim_v = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 170, 173, 175, 180, 183, 190, 190, 200, 205, 205, 210,
             211, 212, 213, 214, 220]
    dim = dict(zip(dim_k, dim_v))

    minimus_d = car_input["crca=r:"]
    maximus_d = car_input["crca_max"]

    car_input["crca=r:"] = dim[int(minimus_d)] if (4000 > int(minimus_d) > 1000) and (int(minimus_d) in dim_k) else 1
    car_input["crca_max"] = dim[int(maximus_d)] if (4000 > int(maximus_d) > 1000) and (int(maximus_d) in dim_k) else 230

    if car_input["cmdl2="] != FSB:
        car_input["cbnd2="] = ""

    new_part = []
    for key in car_input:
        if car_input[key] != FSB:
            new_part.append(str(key) + str(car_input[key]))
    new_part_url = "&".join(new_part).replace("&rgd_max", ",").replace("&prc_max", ",").replace("&crca_max", ",")
    size = REPORT_PARSE_LIMIT_PAGES * 25 if work is True else PARSE_LIMIT_PAGES * 25
    full_url = (
        f"https://api.kufar.by/search-api/v1/search/"
        f"rendered-paginated?cat=2010&sort=lst.d&typ=sell&lang=ru&cur=USD&size={size}&{new_part_url}"
    )
    if car_input["cmdl2="] != FSB:
        full_url = full_url.replace("cbnd2=&", "")
    logging.info(f'<JSON> {full_url}')
    return full_url


@timed_lru_cache(300)
def kufar_url_filter(kufar_link_json):
    kufar_link = ROOT_URL['KUFAR']
    try:
        if '=category_2010.mark_' in kufar_link_json:
            kuf = kufar_link_json.replace('&cmdl2', '').replace('&cbnd2', '').split('=category_2010.mark_')
            kufar_link = kuf[1].replace('_', '-').replace('.model', '')
            kufar_link1, kufar_link2 = kufar_link, ''
            if '&' in kufar_link:
                kufar_link = kufar_link.split('&', 1)
                kufar_link1, kufar_link2 = kufar_link[0], kufar_link[1]
            kuf = kuf[0].split('/')[-1] \
                .replace('rendered-paginated?cat=2010', '').replace('&typ=sell', '').replace('&cur=USD', '')
            kufar_link = f"https://auto.kufar.by/l/cars/{kufar_link1}?cur=USD{kuf}&{kufar_link2}"
    except Exception as e:
        logging.error(f'<kufar_url_filter> {e}')
        return ROOT_URL['KUFAR']
    logging.info(f'<HTML> {kufar_link}')
    return kufar_link
