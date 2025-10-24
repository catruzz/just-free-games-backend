from shutil import which
from dotenv import load_dotenv
from pathlib import Path
from selenium import webdriver
import os
import re
import traceback
load_dotenv()

import django  # nopep8
django.setup()  # nopep8
from backend.api import api  # nopep8
from backend.models import Giveaway  # nopep8

PLATFORMS = api.get_platforms()


def get_selenium_web_driver():
    Path("logs").mkdir(exist_ok=True)
    browser = None
    traceback_infos = []

    def get_firefox_driver():
        from selenium.webdriver.firefox.options import Options
        browser = None
        options = Options()
        options.add_argument('--private')
        options.add_argument('--headless')
        browser = webdriver.Firefox(options=options)
        return browser

    def get_chrome_driver():
        from selenium.webdriver.chrome.options import Options
        browser = None
        options = Options()
        options.add_argument('--incognito')
        options.add_argument('--headless')
        # for selenium >=4.11, explicitly define location of chromium driver.
        if hasattr(webdriver, 'ChromeService'):
            chrome_service_cls = getattr(webdriver, 'ChromeService')
            service = chrome_service_cls(executable_path=which('chromedriver'))
        else:
            service = None
        browser = webdriver.Chrome(options=options, service=service)
        return browser

    if os.environ.get('ENV') == 'development':
        try:
            browser = get_firefox_driver()
            traceback_infos = []
        except Exception:
            traceback_infos.append(traceback.format_exc())
    elif os.environ.get('ENV') == 'production':
        try:
            browser = get_chrome_driver()
            traceback_infos = []
        except Exception:
            traceback_infos.append(traceback.format_exc())

    if len(traceback_infos):
        print("\n".join(traceback_infos))

    return browser


def get_giveaway_platforms(text):
    playstation_found = False
    xbox_found = False
    nintendo_found = False

    platforms = []
    if (re.search(r'\b(steam|humblebundle)\b', text, re.I)):
        temp = find_in_platforms('steam')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bGOG\b', text, re.I)):
        temp = find_in_platforms('gog')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(epic\s*games*|egs)(\s*store)?\b', text, re.I)):
        temp = find_in_platforms('epic_games')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(ubisoft|uplay|ubisoft\s*connect)\b', text, re.I)):
        temp = find_in_platforms('ubisoft_connect')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(blizzard|battle\.?net)\b', text, re.I)):
        temp = find_in_platforms('battle_net')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(origin|(ea|electronic\s*arts)(\s*games)?)\b', text, re.I)):
        temp = find_in_platforms('origin')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bindiegala\b', text, re.I)):
        temp = find_in_platforms('indiegala')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bmicrosoft\b', text, re.I)):
        temp = find_in_platforms('microsoft')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(?!sw)itch(\.?io)?\b', text, re.I)):
        temp = find_in_platforms('itch_io')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\brockstar\b', text, re.I)):
        temp = find_in_platforms('rockstar_games')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\boculus\b', text, re.I)):
        temp = find_in_platforms('oculus')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bpc\b', text, re.I)):
        temp = find_in_platforms('pc')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(ps4|playstation\s*4)\b', text, re.I)):
        playstation_found = True
        temp = find_in_platforms('ps4')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(ps5|playstation\s*5)\b', text, re.I)):
        playstation_found = True
        temp = find_in_platforms('ps5')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(playstation|ps)\b', text, re.I) and not playstation_found):
        playstation_found = True
        temp = find_in_platforms('playstation')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(xb|xbox)\s*(one|1)\b', text, re.I)):
        xbox_found = True
        temp = find_in_platforms('xbox_one')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(xb|xbox)\s*360\b', text, re.I)):
        xbox_found = True
        temp = find_in_platforms('xbox_360')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(xb|xbox)\b', text, re.I) and not xbox_found):
        xbox_found = True
        temp = find_in_platforms('xbox')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bswitch\b', text, re.I)):
        nintendo_found = True
        temp = find_in_platforms('switch')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bnintendo\b', text, re.I) and not nintendo_found):
        temp = find_in_platforms('nintendo')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(amazon|prime\s*(gaming)?)\b', text, re.I)):
        temp = find_in_platforms('amazon')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\blegacy\s*games\b', text, re.I)):
        temp = find_in_platforms('legacy_games')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bstove\b', text, re.I)):
        temp = find_in_platforms('stove')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\b(iOs.*android|android.*iOs|mobile)\b', text, re.I)):
        temp = find_in_platforms('mobile')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\biOs\b', text, re.I)):
        temp = find_in_platforms('ios')
        if temp:
            platforms.append(temp["id"])
    if (re.search(r'\bandroid\b', text, re.I)):
        temp = find_in_platforms('android')
        if temp:
            platforms.append(temp["id"])

    # remove duplicates
    platforms = list(set(platforms))

    return platforms if platforms else None


def find_in_platforms(text):
    return next((item for item in PLATFORMS if item["id"] == text), None)


def get_giveaway_type(text):
    if (re.search(r'\b(pack|gift|crate|skin|kit|loot)s?\b', text, re.I)):  # TODO: add XP?
        temp = Giveaway.Type.LOOT
    elif (re.search(r'\b(dlc)s?\b', text, re.I)):
        temp = Giveaway.Type.DLC
    elif (re.search(r'\bbeta\b', text, re.I)):
        temp = Giveaway.Type.BETA
    elif (re.search(r'\balpha\b', text, re.I)):
        temp = Giveaway.Type.ALPHA
    elif (re.search(r'\bmembership\b', text, re.I)):
        temp = Giveaway.Type.MEMBERSHIP
    elif (re.search(r'\bdemo\b', text, re.I)):
        temp = Giveaway.Type.DEMO
    elif (re.search(r'\bgame\b', text, re.I)):
        temp = Giveaway.Type.GAME
    else:
        temp = Giveaway.Type.OTHER

    return temp


def get_giveaway_title(text):
    keywords = [
        r'keys?', r'giveaway',
        r'demo', r'dlc', r'(closed)*\s*beta', r'(closed)*\s*alpha', r'preview', r'in-?\s?game', r'game(?!\s+(pack|of))',
        r'(on\s*)*steam', r'(on\s*)*gog', r'(on\s*)*epic\s*(games\s*)*(store\s*)*', r'(on\s*)*egs',
        r'(on\s*)*uplay', r'(on\s*)*ubisoft\s*connect', r'(on\s*)*ubisoft',
        r'(on\s*)*pc', r'(on\s*)*playstation', r'(on\s*)*ps4', r'(on\s*)*ps5',
        r'(on\s*)*(xb?|xbox)\s*(360|one|1)*', r'(on\s*)*(nintendo)*\s*switch'
    ]
    for word in keywords:
        regex = re.compile(rf'\b{word}\b', re.I)
        text = regex.sub('', text)
    text = re.sub(r'\(\W*\)', ' ', text)
    text = re.sub(r'\!*\¡*\?*\¿*', '', text)
    text = re.sub(r'\s\s*', ' ', text)
    return text.strip()
