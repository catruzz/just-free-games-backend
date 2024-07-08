from datetime import datetime
from backend.scraper.utils import lib
import requests
import time
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    base_url = 'https://www.epicgames.com'
    giveaways_url = 'https://www.epicgames.com/store/en-US/free-games?lang=en-US'
    api_url = 'https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US'
    now = datetime.now()

    try:
        response = requests.get(api_url)
        time.sleep(0.5)
        json = response.json()
        giveaway_platforms = lib.get_giveaway_platforms('EpicGames')
        giveaway_type = lib.get_giveaway_type('Game')
        for el in json['data']['Catalog']['searchStore']['elements']:
            effective_date = datetime.strptime(
                el['effectiveDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
            if el['price']['totalPrice']['discountPrice'] == 0 and now > effective_date:
                try:
                    expiration_date = datetime.strptime(
                        el['price']['lineOffers'][0]['appliedRules'][0]['endDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
                except:
                    expiration_date = None
                product_slug = el['productSlug'] if el['productSlug'] else el['offerMappings'][0]['pageSlug']
                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': el['title'],
                    'url': base_url+"/store/en-US/p/"+product_slug,
                    'description': '',
                    'supplier': supplier_id,
                    'expiration_date': expiration_date,
                    'msrp': el['price']['totalPrice']['originalPrice'] / 100,
                    'post_id': el['id'],
                    'post_title': el['title'],
                    'post_url': giveaways_url,
                    'post_image': el['keyImages'][0]['url'],
                })

#         page = requests.get(giveaways_url)
#         time.sleep(0.5)
#         soup = BeautifulSoup(page.content, 'html.parser')
#         for link in soup.find_all('a', attrs={'aria-label': re.compile('(^More Free Games|^Free to Play)')}):
#             giveaway_title = link.find(
#                 'span', attrs={'data-component': 'OfferTitleInfo'}).string
#             giveaways.append({
#                 'platforms': giveaway_platforms,
#                 'type': giveaway_type,
#                 'title': giveaway_title,
#                 'url': base_url+link['href'],
#                 'description': '(Free to Play)',
#                 'supplier': supplier_id,
#                 'post_id': '',
#                 'post_title': giveaway_title,
#                 'post_url': giveaways_url,
#                 'post_image': link.find('img')['data-image'],
#             })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
