from bs4 import BeautifulSoup
import requests
import traceback

import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway

from backend.scraper.utils import lib


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://itch.io/games/newest/on-sale'

    try:
        page = requests.get(giveaways_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        giveaway_platforms = lib.get_giveaway_platforms('itch.io')
        giveaway_type = Giveaway.Type.GAME

        for item in soup.find_all('div', class_='game_cell'):
            sale_tag = item.find('div', class_='sale_tag').string
            if sale_tag == '-100%':
                image = item.find('div', class_='game_thumb').find(
                    'a', class_='thumb_link').find('img')
                link = item.find('a', class_='title')
                giveaway_title = link.string
                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': giveaway_title,
                    'url': link['href'],
                    'description': '',
                    'supplier': supplier_id,
                    'post_id': item['data-game_id'],
                    'post_title': giveaway_title,
                    'post_url': giveaways_url,
                    'post_image': image['data-lazy_src'],
                })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
