from datetime import datetime
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import traceback
import time

import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway
from backend.scraper.utils import lib
from backend.api import api


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://gaming.amazon.com'

    timeout = 15

    browser = lib.get_selenium_web_driver()
    if not browser:
        return giveaways
    browser.get(giveaways_url+'/home')
    time.sleep(timeout)
    browser.execute_script(
        'const sleep = (ms) => {' +
        '  return new Promise((resolve) => setTimeout(resolve, ms));' +
        '};' +
        'const check = async () => {' +
        '  let i = 0;' +
        '  let end = false;' +
        '  while (!end) {' +
        '    const a = document.getElementsByClassName("item-card__action");' +
        '    if (a[i]) {' +
        '      a[i].scrollIntoView();' +
        '      i++;' +
        '      await sleep(200);' +
        '    } else {' +
        '      end = true;' +
        '    }' +
        '  }' +
        '};' +
        'check();')
    time.sleep(timeout*4)

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'offer-list__content'))
        )
    except TimeoutException:
        pass
    finally:
        page_source = browser.page_source

    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        sections = soup.find_all('div', class_='offer-list__content')

        # check previous giveaways to avoid rescraping them
        previous_giveaways = api.get_giveaways(supplier='amazon')
        scraped_urls = list(map(lambda x: str(x['url']), previous_giveaways))

        for section in sections:
            items = []
            data_a_target = section.get('data-a-target')
            if data_a_target == 'offer-section-FGWP_FULL':
                giveaway_type = Giveaway.Type.GAME
            elif data_a_target == 'offer-section-IN_GAME_LOOT':
                giveaway_type = Giveaway.Type.LOOT
            else:
                continue

            items = section.find_all('div', class_='item-card__action')
            for item in items:
                link = item.find('a')
                # makes each giveaway link unique
                url = giveaways_url
                if link:
                    url += link['href']
                else:
                    url += '#' + item['aria-label'].replace(" ", "")

                giveaway_platforms = lib.get_giveaway_platforms(
                    'amazon')
                expiration_date = None
                if giveaway_type == Giveaway.Type.GAME and url not in scraped_urls:
                    #  keep track of scraped url
                    scraped_urls.append(url)
                    browser.get(url)
                    time.sleep(0.5)
                    try:
                        WebDriverWait(browser, timeout).until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, 'description__item-detail'))
                        )
                    except TimeoutException:
                        pass
                    finally:
                        page_source = browser.page_source
                    soup = BeautifulSoup(page_source, 'html.parser')

                    try:
                        availability_date = soup.find(
                            'div', class_='availability-date')
                        spans = availability_date.find_all('span')
                        expiration_date = datetime.strptime(
                            spans[1].text, '%b %d, %Y')
                    except:
                        pass

                    description = soup.find(
                        'div', class_='description__item-detail')
                    if description:
                        giveaway_platforms_temp = lib.get_giveaway_platforms(
                            description.text)
                        if giveaway_platforms_temp is not None:
                            if 'pc' in giveaway_platforms_temp:
                                giveaway_platforms_temp.remove('pc')
                            giveaway_platforms = giveaway_platforms_temp

                giveaway_title_container = item.find(
                    'div', class_='item-card-details__body')
                giveaway_title = ''
                if data_a_target == 'offer-section-IN_GAME_LOOT':
                    giveaway_title += giveaway_title_container.find(
                        'p').text + ' - '
                giveaway_title += giveaway_title_container.find('h3').text
                image = item.find('img')
                # images are not loaded in case of low bandwidth
                image_src = image['src'] if image else ''
                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': giveaway_title,
                    'url': url,
                    'description': 'Amazon Prime Gaming membership required',
                    'supplier': supplier_id,
                    'expiration_date': expiration_date,
                    'post_id': giveaway_title,
                    'post_title': giveaway_title,
                    'post_url': giveaways_url,
                    'post_image': image_src,
                })
    except Exception:
        traceback.print_exc()
        raise

    browser.quit()
    return giveaways
