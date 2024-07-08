from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from backend.scraper.utils import lib
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://www.gog.com'

    timeout = 5

    browser = lib.get_selenium_web_driver()
    if not browser:
        return giveaways
    browser.get(giveaways_url)

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, 'giveaway'))
        )
    except TimeoutException:
        pass
    finally:
        page_source = browser.page_source
        browser.quit()

    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        giveaway_banner = soup.find('div', id='giveaway')

        expiration_date = None
        try:
            time_left = soup.find('countdown', class_='giveaway__countdown')
            time_left = time_left.text.replace(
                'left', '').replace(' ', '').split(':')
            expiration_date = datetime.now() + timedelta(
                hours=int(time_left[0]), minutes=int(time_left[1]))
        except:
            pass

        if giveaway_banner:
            link = giveaway_banner.find('a', class_='giveaway__overlay-link')
            if not link:
                return giveaways

            text = giveaway_banner.find(
                'div', class_='giveaway__content-header').get_text().strip()
            giveaway_platforms = lib.get_giveaway_platforms('gog')
            giveaway_type = lib.get_giveaway_type('Game')
            giveaway_title = text.replace('Giveaway: Claim ', '').replace(
                ' and don\'t miss the best GOG offers!', '')

            image_container = giveaway_banner.find(
                'div', class_='giveaway__image')
            if image_container:
                image = image_container.find('source', type='image/jpeg')
                if image:
                    image = image['srcset'].split(',')[0]
            if text:
                giveaways.append({
                    'platforms': giveaway_platforms,
                    'type': giveaway_type,
                    'title': giveaway_title,
                    'url': link['href'],
                    'description': '',
                    'supplier': supplier_id,
                    'expiration_date': expiration_date,
                    'post_id': '',
                    'post_title': giveaway_title,
                    'post_url': giveaways_url,
                    'post_image': image,
                })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
