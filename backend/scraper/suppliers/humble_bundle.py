from bs4 import BeautifulSoup
from backend.scraper.utils import lib
import requests
import time
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://www.humblebundle.com'

    try:
        page = requests.get(giveaways_url)
        time.sleep(0.5)
        soup = BeautifulSoup(page.content, 'html.parser')

        banner = soup.find('div', attrs={'id': 'site-xpromo-banner'})
        if banner:
            link = banner.find('a')
            text = link.find('p').find('strong')
            if not text:
                return []
            giveaway_title = text.string.replace(
                'Click here to get ', '').replace('FREE for a limited time!', '')
            page2 = requests.get(link['href'])
            time.sleep(0.5)
            soup2 = BeautifulSoup(page2.content, 'html.parser')
            text = soup2.find('div', class_='blurb-text')
            if text:
                giveaway_platforms = lib.get_giveaway_platforms(text.string)
                giveaway_type = lib.get_giveaway_type('Game')
                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': giveaway_title,
                    'url': link['href'],
                    'description': '',
                    'supplier': supplier_id,
                    'post_id': '',
                    'post_title': giveaway_title,
                    'post_url': giveaways_url,
                })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
