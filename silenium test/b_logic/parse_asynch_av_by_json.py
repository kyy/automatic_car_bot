import asyncio
import json

import numpy as np
from aiohttp import ClientSession
import requests
from multiprocessing import Pool
from time import sleep


root = 'https://api.av.by/offer-types/cars/filters/main/init?'
url = 'https://api.av.by/offer-types/cars/filters/main/init?brands[0][brand]=6'



def json_load_av_by():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/103.0.0.0 Safari/537.36',
        'accept': '*/*'}
    r = requests.get(url, headers=headers).json()
    page_count = r['pageCount']
    print(page_count)
    adverts = r['adverts']
    i = 1
    if page_count > 1:
        while page_count > 1:
            i += 1
            r = requests.get(f'{url}&page={i}', headers=headers).json()
            adverts.append(r['adverts'])
            print(page_count)
            page_count -= 1
    return adverts


def json_write_av_by():
    with open('json/av_by.txt', 'w') as outfile:
        json.dump(json_load_av_by(), outfile)


def json_parse_av_by():
    with open('json/av_by.txt') as json_file:
        data = json.load(json_file)
    count = data['count']
    page_count = data['pageCount']
    print(count, page_count)

def main():
    json_write_av_by()



if __name__ == "__main__":
    main()
