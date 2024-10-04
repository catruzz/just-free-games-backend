from bs4 import BeautifulSoup
from backend.scraper.utils import lib
import datetime
import re
import requests
import time
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    base_url = 'https://www.playstation.com'
    giveaways_url = 'https://www.playstation.com/en-us/ps-plus/whats-new/'

    try:
        page = requests.get(giveaways_url)
        time.sleep(0.5)
        soup = BeautifulSoup(page.content, 'html.parser')

        giveaway_type = lib.get_giveaway_type('Game')

        monthly_games = soup.find('section', id='monthly-games')
        for item in monthly_games.find_all('div', class_='box--light'):
            title = item.find('h3')
            if title is None:
                continue
            giveaway_title = title.string.strip()
            image = item.find('picture', class_='media-block__img')
            if image is not None:
                image = image.find_all('source')[2]['srcset']
            link = item.find('a', class_='btn--cta')
            if link is None:
                continue
            href = link['href']
            if 'https' not in href:
                href = base_url + href
            page2 = requests.get(href)
            time.sleep(0.5)
            soup2 = BeautifulSoup(page2.content, 'html.parser')

            platforms = ''
            platforms_container = soup2.find('div', class_="platform-badge")
            if platforms_container:
                for platform in platforms_container.find_all('span'):
                    platforms += platform.string.strip() + ' '
            else:
                platforms += 'PS4'

            giveaway_platforms = lib.get_giveaway_platforms(platforms)

            # set expiration date to the second day of the next month
            expiration_date = (datetime.datetime.today().replace(day=1) +
                               datetime.timedelta(days=32)).replace(day=2, hour=0, minute=0, second=0, microsecond=0)

            # loop over radio buttons to find the MSRP
            msrp = None
            for i in range(3):
                msrp_container = None
                msrp_container = soup2.find(
                    'span', {'data-qa': f'mfeCtaMain#offer{i}#finalPrice'})
                if msrp_container is not None:
                    # find numbers in text
                    msrps = re.findall(r'[\d]*[.][\d]+', msrp_container.text)
                    if len(msrps) > 0:
                        msrp = float(msrps[0])
                        break

            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': href,
                'description': 'PlayStation®Plus membership required',
                'supplier': supplier_id,
                'expiration_date': expiration_date,
                'msrp': msrp,
                'post_id': giveaway_title,
                'post_title': giveaway_title,
                'post_url': giveaways_url,
                'post_image': image,
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
