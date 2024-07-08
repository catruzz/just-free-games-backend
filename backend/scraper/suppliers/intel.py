from backend.scraper.utils import lib
import re
import requests
import time
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://game.intel.com/ww/giveaways'
    api_url = 'https://game.intel.com/api/giveaways?displayType=homepage&range=%5B0%2C50%5D'

    try:
        response = requests.get(api_url)
        time.sleep(0.5)
        json = response.json()
        for el in json['giveaways']:
            if el['endsInDays'] < 0:
                continue
            title = el['title']
            if (re.search(r'(sweepstakes?|challenges?)', title, re.I)):
                continue
            image = f'https://game.intel.com/assets/giveaways/{el["id"]}/{el["imgNames"]["largeThumb"]}'
            giveaway_platforms = lib.get_giveaway_platforms(title)
            if giveaway_platforms == None:
                giveaway_platforms = lib.get_giveaway_platforms(
                    el['shortDescription'])
            giveaway_type = lib.get_giveaway_type(title)
            giveaway_title = lib.get_giveaway_title(title)

            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': giveaways_url + '/' + el['seoName'],
                'description': '',
                'supplier': supplier_id,
                'post_id': '',
                'post_title': title,
                'post_url': giveaways_url,
                'post_image': image,
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
