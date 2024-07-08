import re
import requests
import time
import traceback
from bs4 import BeautifulSoup
from json import loads as JSON

from backend.scraper.utils import lib
import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway  # nopep8
from backend.api import api

giveaways = []


def get_giveaway(supplier_id, url, el):
    try:
        page = requests.get(url)
        time.sleep(0.5)
        soup = BeautifulSoup(page.content, 'html.parser')

        # looks for required level and keys left
        pattern = r'var\s*countryKeys\s*=\s*(.*?);'
        country_keys_script = soup.find(
            "script", type="text/javascript", string=re.compile(pattern))
        if not country_keys_script:
            return False

        country_keys = re.search(pattern, country_keys_script.string).group(1)
        parsed = JSON(country_keys)
        if len(parsed) == 0:
            return False

        key_pair = parsed['US']

        required_level = 0
        keys_left = 0
        if len(key_pair):
            if type(key_pair) is list:
                keys_left = key_pair[0]
            elif type(key_pair) is dict:
                for key in key_pair:
                    required_level = int(key)
                    keys_left = key_pair[key]

        # skip ended giveaways
        if not keys_left:
            return False

        giveaway_platforms = lib.get_giveaway_platforms(el['instructions'])
        if giveaway_platforms == None:
            giveaway_platforms = lib.get_giveaway_platforms(el['description'])
            if giveaway_platforms == None:
                giveaway_platforms = lib.get_giveaway_platforms(el['title'])
        giveaway_type = lib.get_giveaway_type(el['title'])
        giveaway_title = lib.get_giveaway_title(el['title'])

        giveaways.append({
            'platforms': giveaway_platforms,
            'type': giveaway_type,
            'title': giveaway_title,
            'url': url,
            'description': f'Alienware level {required_level}+ membership required' if required_level > 1 else '',
            'supplier': supplier_id,
            'post_id': el['id'],
            'post_title': el['title'],
            'post_url': url,
            'post_image': el['image'],
        })

    except Exception:
        traceback.print_exc()
        raise


def get_giveaways(supplier_id):
    base_url = 'https://na.alienwarearena.com'
    api_url = 'https://na.alienwarearena.com/esi/featured-tile-data/Giveaway'

    # check expired and canceled giveaways to avoid rescraping them: published and created giveaways are scraped to update status if needed
    expired_and_canceled_giveaways = api.get_giveaways(
        status=[Giveaway.Status.EXPIRED, Giveaway.Status.CANCELED], supplier='alienware')
    scraped_urls = list(
        map(lambda x: str(x['url']), expired_and_canceled_giveaways))

    try:
        last_page = 2  # increment this to get older giveaways
        for x in range(1, last_page):
            response = requests.get(f'{api_url}/{x}')
            json = response.json()
            for el in json['data']:
                url = base_url+el['url']
                if url not in scraped_urls:
                    get_giveaway(supplier_id, url, el)
                    #  keep track of scraped url
                    scraped_urls.append(url)
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
