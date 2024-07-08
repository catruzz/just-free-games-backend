import json
from typing import List
from dotenv import load_dotenv
import os
import requests
load_dotenv()

from backend.models import Giveaway  # nopep8

API_URL = 'https://api.isthereanydeal.com/'
API_URL_IDENTIFIER = f"{API_URL}games/lookup/v1"
API_URL_PRICES = f"{API_URL}games/prices/v2"
API_URL_DEALS = f"{API_URL}deals/v2"


def get_identifiers(titles: List[str]) -> List[str]:
    ids_map = []
    for title in titles:
        response = requests.get(
            url=API_URL_IDENTIFIER,
            params={
                'key': os.environ.get('ITAD_API_KEY'),
                'title': title
            }
        )
        response.raise_for_status()
        try:
            game = response.json()['game']
            id = game['id']
            ids_map.append({'id': id, 'title': title})
        except:
            continue
    return ids_map


def get_prices(titles: List[str] = [], ids: List[str] = []):
    prices_map = []
    if not titles and not ids:
        return {}
    if titles and not ids:
        ids_map = get_identifiers(titles)
        ids = list(map(lambda x: str(x['id']), ids_map))
    if not ids:
        return {}
    response = requests.post(
        url=API_URL_PRICES,
        headers={'Content-Type': 'application/json',
                 'Accept': 'application/json'},
        params={
            'key': os.environ.get('ITAD_API_KEY'),
            'nondeals': True,
        },
        data=json.dumps(ids)
    )
    response.raise_for_status()
    for row in response.json():
        id = row['id']
        price = row['deals'][0]['regular']['amount']
        title = next(item['title'] for item in ids_map if item['id'] == id)
        prices_map.append({'id': id, 'price': price, 'title': title})
    return prices_map


def get_deals(max_pages: int = 5):
    offset = 0
    limit = 20
    go_on = True
    deals = []
    while go_on:
        response_temp = requests.get(
            url=API_URL_DEALS,
            params={
                'key': os.environ.get('ITAD_API_KEY'),
                'sort': '-cut',
                'limit': limit,
                'offset': offset,
                # 'shops': '61,35' # steam, gog
            }
        )
        response_temp.raise_for_status()
        response = response_temp.json()
        if response['hasMore'] is False:
            go_on = False
        items = response['list']
        offset = offset + limit
        for item in items:
            # be sure that deal price is == 0 since sometimes it's not, even if cut is 100
            if int(item['deal']['price']['amount']) == 0:
                deals.append(item)
            if offset >= limit * max_pages or int(item['deal']['cut']) != 100:
                go_on = False
                break
    return deals
