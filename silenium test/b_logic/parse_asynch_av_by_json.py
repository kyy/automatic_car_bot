import asyncio
import json

import numpy as np
from aiohttp import ClientSession
import requests
from multiprocessing import Pool
from time import sleep


root = 'https://api.av.by/offer-types/cars/filters/main/init?'
url = 'https://api.av.by/offer-types/cars/filters/main/init?brands[0][brand]=43&engine_type[0]=5&year[min]=2016'



def json_load_av_by():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103.0.0.0 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(url, headers=headers).json()
    page_count = r['pageCount']
    count = r['count']
    adverts = r['adverts']
    i = 1
    if page_count > 1:
        while page_count > 1:
            i += 1
            r = requests.get(f'{url}&page={i}', headers=headers).json()
            for j in range(len(r['adverts'])):
                adverts.append(r['adverts'][j])
            page_count -= 1
            print(page_count)
    return adverts, count


def json_write_av_by():
    with open('json/av_by.txt', 'w') as outfile:
        json.dump(json_load_av_by(), outfile)


def json_parse_av_by():
    with open('json/av_by.txt') as json_file:
        data = json.load(json_file)


def main():
    json_write_av_by()



if __name__ == "__main__":
    main()
