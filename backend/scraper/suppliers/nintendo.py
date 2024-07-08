from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from backend.scraper.utils import lib
import re
import traceback

import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://www.nintendo.com/store/games/?p=1&sort=pa&f=priceRange&priceRange=%240+-+%244.99'

    timeout = 5

    browser = lib.get_selenium_web_driver()
    if not browser:
        return giveaways
    browser.get(giveaways_url)

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'game-list-results-container'))
        )
    except TimeoutException:
        pass
    finally:
        page_source = browser.page_source
        browser.quit()

    try:
        soup = BeautifulSoup(page_source, 'html.parser')

        giveaway_platforms = lib.get_giveaway_platforms('switch')
        giveaway_type = Giveaway.Type.GAME

        items_container = soup.find('div', class_=re.compile(
            'SearchLayout__FilterResultsGrid.*'))
        for link in items_container.find_all('a', class_=re.compile('BasicTilestyles__Tile.*')):
            msrp = link.find('span', class_=re.compile(
                'Pricestyles__MSRP.*'))
            price = [int(i) for i in re.findall(r'\d+', msrp.text)]
            if sum(price) != 0:
                return giveaways
            title = link.find('h2', class_=re.compile(
                'Headingstyles__Styled.*')).string
            image = link.find('img')

            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': title,
                'url': link['href'],
                'description': '',
                'supplier': supplier_id,
                'post_id': title,
                'post_title': title,
                'post_url': giveaways_url,
                'post_image': image['src'],
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
