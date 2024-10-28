from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from backend.scraper.utils import lib
import traceback


def get_giveaways(supplier_id):
    giveaways = []
    giveaways_url = 'https://www.mmobomb.com/giveaway/'

    timeout = 5

    browser = lib.get_selenium_web_driver()
    if not browser:
        return giveaways
    browser.get(giveaways_url)

    try:
        WebDriverWait(browser, timeout).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'content_area')))
    except TimeoutException:
        pass
    finally:
        page_source = browser.page_source
        browser.quit()

    try:
        soup = BeautifulSoup(page_source, 'html.parser')

        for item in soup.find_all('article', class_='content'):
            button = item.find('button', type='button')
            if not button or button.text.strip() != "Open":
                continue
            image = item.find('img', class_='card-img-top')
            link = item.find('a')
            title = link.string
            giveaway_platforms = lib.get_giveaway_platforms(title)
            giveaway_type = lib.get_giveaway_type(title)
            giveaway_title = lib.get_giveaway_title(title)

            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': link['href'],
                'description': '',
                'supplier': supplier_id,
                'post_id': giveaway_title,
                'post_title': title,
                'post_url': giveaways_url,
                'post_image': image['src'],
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
