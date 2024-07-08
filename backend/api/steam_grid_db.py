from typing import List
from dotenv import load_dotenv
import os
import requests
load_dotenv()

API_URL = 'https://www.steamgriddb.com/api/v2/'
API_URL_GAME_SEARCH = f"{API_URL}search/autocomplete/"
API_URL_GRIDS = f"{API_URL}grids/game/"

HEADERS = {
    'Authorization': f'Bearer {os.environ.get("STEAM_GRID_DB_API_KEY")}'}


def get_grids(game_names: List[str]) -> List[dict]:
    grids = []
    for game_name in game_names:
        response = requests.get(
            url=API_URL_GAME_SEARCH + game_name,
            headers=HEADERS,
        )
        response.raise_for_status()
        data = response.json()
        if not data or 'data' not in data or not data['data']:
            # add empty string to match the length of game_names
            grids.append('')
            continue
        data = data['data']
        game_id = data[0]['id']
        response = requests.get(
            url=API_URL_GRIDS + str(game_id),
            headers=HEADERS,
            params={
                'dimensions': '920x430,460x215'
            }
        )
        response.raise_for_status()
        data = response.json()
        if not data or 'data' not in data or not data['data']:
            # add empty string to match the length of game_names
            grids.append('')
            continue
        data = data['data'][0]
        grids.append(data['url'])
    return grids
