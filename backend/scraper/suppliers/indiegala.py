from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from backend.scraper.utils import lib
import re
import requests
import time
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    giveaways += get_giveaways_freebies(supplier_id)
    # showcase items are always free elsewhere
    # giveaways += get_giveaways_showcase(supplier_id)
    return giveaways


def get_giveaways_freebies(supplier_id):
    giveaways = []
    giveaways_url = 'https://freebies.indiegala.com/'

    timeout = 5

    browser = lib.get_selenium_web_driver()
    if not browser:
        return giveaways
    browser.get(giveaways_url)

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'products-col-inner'))
        )
    except TimeoutException:
        pass
    finally:
        page_source = browser.page_source
        browser.quit()

    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        giveaway_platforms = lib.get_giveaway_platforms('Indiegala')
        giveaway_type = lib.get_giveaway_type('Game')
        for item in soup.find_all('div', class_='products-col-inner'):
            link = item.find('a', class_='fit-click')
            image = item.find('img')
            post_id = re.search(
                r'products\/(.*)\/prodmain', image['data-img-src']).group(1)
            giveaway_title = item.find('div', class_='product-title').string
            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': link['href'],
                'description': '',
                'supplier': supplier_id,
                'post_id': post_id,
                'post_title': giveaway_title,
                'post_url': giveaways_url,
                'post_image': image['data-img-src'],
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways


def get_giveaways_showcase(supplier_id):
    giveaways = []
    base_url = 'https://www.indiegala.com/showcase'
    api_url = 'https://www.indiegala.com/showcase/ajax'
    giveaway_platforms = lib.get_giveaway_platforms('Indiegala')
    giveaway_type = lib.get_giveaway_type('Game')

    page = 0
    while True:
        try:
            page += 1
            api_url_temp = f'{api_url}/{page}'
            response = requests.get(api_url_temp)
            time.sleep(0.5)
            json = response.json()
            soup = BeautifulSoup(json['html'], 'html.parser')

            items = soup.find_all('div', class_='main-list-item-col')
            if len(items) == 0:
                break

            for item in items:
                link = item.find('a', class_='main-list-item-clicker')
                image = item.find('img', class_='img-fit')
                post_id = re.search(
                    r'products\/(.*)\/prodmain', image['data-img-src']).group(1)
                giveaway_title = item.find(
                    'div', class_='showcase-title').string
                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': giveaway_title,
                    'url': link['href'],
                    'description': '',
                    'supplier': supplier_id,
                    'post_id': post_id,
                    'post_title': giveaway_title,
                    'post_url': base_url,
                    'post_image': image['data-img-src'],
                })
        except Exception:
            traceback.print_exc()
            raise

        # if something goes wrong
        if page == 0 or page == 10:
            break

    return giveaways
