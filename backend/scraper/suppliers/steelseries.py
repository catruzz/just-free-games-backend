from backend.scraper.utils import lib
import requests
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    base_url = 'https://games.steelseries.com/'
    api_url = 'https://api.igsp.io/promotions'

    try:
        response = requests.get(api_url)
        json = response.json()
        for el in json:
            if el['active'] is True and el['percentRemaining'] != 0:
                giveaway_platforms = lib.get_giveaway_platforms(
                    '\n'.join(el['instructions']))
                if giveaway_platforms == None:
                    giveaway_platforms = lib.get_giveaway_platforms(
                        el['platform'])
                giveaway_type = lib.get_giveaway_type(el['title'])
                giveaway_title = lib.get_giveaway_title(el['title'])

                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': giveaway_title,
                    'url': base_url+'giveaway/'+str(el['id'])+'/overview',
                    'description': '',
                    'supplier': supplier_id,
                    'post_id': el['uuid'],
                    'post_title': el['title'],
                    'post_url': base_url,
                    'post_image': el['imageUrl'],
                })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
