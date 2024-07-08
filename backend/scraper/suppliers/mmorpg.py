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
    base_url = 'https://www.mmorpg.com'
    giveaways_url = 'https://www.mmorpg.com/giveaways'
    keys_api_url = 'https://www.mmorpg.com/ajax/tools.cfc?method=key_counts&gids='

    timeout = 10

    browser = lib.get_selenium_web_driver()
    if not browser:
        return giveaways
    browser.get(giveaways_url)
    time.sleep(timeout)

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'item__tile'))
        )
    except TimeoutException:
        pass
    finally:
        page_source = browser.page_source
        browser.quit()

    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        keys = soup.find_all('a', {"data-giveaway": re.compile('\d+')})
        gids = []
        for key in keys:
            gids.append(key['data-giveaway'])
        keys_api_url += ','.join(gids)
        response = requests.get(keys_api_url)
        time.sleep(0.5)
        # json = response.json()
        for item in soup.find_all('div', class_='item__tile'):
            gid = item.find('a', {"data-giveaway": re.compile('\d+')})
            if gid['data-giveaway'] == 0:
                continue
            image = item.find('img')
            link = item.find('div', class_='item__content__title').find(
                'h3').find('a')
            title = link.string
            post_id = item.find('time')['datetime']
            giveaway_platforms = lib.get_giveaway_platforms(title)
            giveaway_type = lib.get_giveaway_type(title)
            giveaway_title = lib.get_giveaway_title(title)

            if giveaway_platforms == None:
                page2 = requests.get(base_url+link['href'])
                time.sleep(0.5)
                soup2 = BeautifulSoup(page2.content, 'html.parser')
                text = soup2.find('div', class_='single-page')
                if text:
                    giveaway_platforms = lib.get_giveaway_platforms(
                        text.get_text())

            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': base_url+link['href'],
                'description': '',
                'supplier': supplier_id,
                'post_id': post_id,
                'post_title': title,
                'post_url': giveaways_url,
                'post_image': 'https:'+image['src'],
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
