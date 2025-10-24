from django.test import TestCase
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


class LibTest(TestCase):
    # def setUp(self):

    def test_scrape_page_with_beautifulsoup(self):
        """Correctly scrape page with BeautifulSoup"""
        url = 'https://www.google.com/'

        timeout = 5

        browser = lib.get_selenium_web_driver()
        self.assertIsNotNone(browser)
        browser.get(url)

        try:
            WebDriverWait(browser, timeout).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, 'body'))
            )
        except TimeoutException:
            raise
        finally:
            page_source = browser.page_source
            browser.quit()

        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            self.assertIsNotNone(soup)
            script = soup.find("script")
            self.assertIsNotNone(script)
        except Exception:
            traceback.print_exc()
            raise
