#! usr/bin/env python3
from datetime import datetime, timedelta
import math
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from dotenv import load_dotenv
import concurrent.futures
import sys
import time
import traceback
load_dotenv()

import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway  # nopep8
from backend.api import api, is_there_any_deal, steam_grid_db  # nopep8

SUPPLIERS = api.get_suppliers()
SCRAPE_TIME_BY_SUPPLIER = {}
NOW = timezone.now()
NOW_ROUNDED_DOWN_TO_NEAREST_5_MINUTES = NOW.replace(
    minute=5 * math.floor(NOW.minute / 5),
    second=0,
    microsecond=0)


def supplier_matches(supplier, title):
    return 'id' in supplier and supplier['id'] == title


def get_giveaways(supplier):
    giveaways = []
    traceback_info = None
    try:
        if supplier_matches(supplier, title='alienware'):
            from backend.scraper.suppliers import alienware as sup
        elif supplier_matches(supplier, title='amazon'):
            from backend.scraper.suppliers import amazon as sup
        elif supplier_matches(supplier, title='epic_games'):
            from backend.scraper.suppliers import epic_games as sup
        elif supplier_matches(supplier, title='gog'):
            from backend.scraper.suppliers import gog as sup
        elif supplier_matches(supplier, title='humble_bundle'):
            from backend.scraper.suppliers import humble_bundle as sup
        elif supplier_matches(supplier, title='indiegala'):
            from backend.scraper.suppliers import indiegala as sup
        elif supplier_matches(supplier, title='intel'):
            from backend.scraper.suppliers import intel as sup
        elif supplier_matches(supplier, title='is_there_any_deal'):
            from backend.scraper.suppliers import is_there_any_deal as sup
        elif supplier_matches(supplier, title='itch_io'):
            from backend.scraper.suppliers import itch_io as sup
        elif supplier_matches(supplier, title='mmobomb'):
            from backend.scraper.suppliers import mmobomb as sup
        elif supplier_matches(supplier, title='mmorpg'):
            from backend.scraper.suppliers import mmorpg as sup
        elif supplier_matches(supplier, title='reddit'):
            from backend.scraper.suppliers import reddit as sup
        elif supplier_matches(supplier, title='playstation'):
            from backend.scraper.suppliers import playstation as sup
        elif supplier_matches(supplier, title='steelseries'):
            from backend.scraper.suppliers import steelseries as sup
        elif supplier_matches(supplier, title='nintendo'):
            from backend.scraper.suppliers import nintendo as sup
        else:
            raise Exception(f'no matching supplier provided ({supplier})')

        # skip this supplier if scrape_frequency is not past yet
        perform_scrape = True
        last_scrape_at = supplier['last_scrape_at']
        if last_scrape_at != None:
            next_scrape_at = parse_datetime(
                last_scrape_at) + timedelta(seconds=supplier['scrape_frequency'])
            if next_scrape_at > NOW:
                perform_scrape = False

        if perform_scrape:
            t0 = time.time()
            giveaways = sup.get_giveaways(supplier_id=supplier["id"])
            t1 = time.time()

            # updates last_scrape_at
            supplier['last_scrape_at'] = NOW_ROUNDED_DOWN_TO_NEAREST_5_MINUTES
            api.update_supplier(supplier)
            SCRAPE_TIME_BY_SUPPLIER[supplier['id']] = t1 - t0
    except Exception:
        traceback_info = traceback.format_exc()

    return giveaways, traceback_info


def mark_as_expired(giveaways):
    default_time_delta = timedelta(days=1)

    published_giveaways = api.get_giveaways(
        status=Giveaway.Status.PUBLISHED,
        limit=1000,
        order_by='-created_at',
    )
    expired = []
    expired_ids = []

    # do not mark as expired if the first giveaway found (ordered by created_at desc) is older than default_time_delta
    if len(published_giveaways) > 0 and parse_datetime(published_giveaways[0]['created_at']) > NOW - default_time_delta:
        giveaways_url = list(map(lambda x: str(x['url']), giveaways))
        filtered = list(
            filter(lambda i: i['url'] not in giveaways_url, published_giveaways))
        for fil in filtered:
            if fil['id'] in expired_ids:
                continue
            # skip giveaways already having expiration_date
            if 'expiration_date' in fil and fil['expiration_date'] is not None:
                if parse_datetime(fil['expiration_date']) < NOW:
                    expired.append(fil)
                    expired_ids.append(fil['id'])
                continue
            time_delta = default_time_delta
            if fil['supplier']:
                supplier = next(
                    (item for item in SUPPLIERS if item["id"] == fil['supplier']), None)
                if supplier is not None and supplier['scrape_frequency'] >= 3600:
                    time_delta = timedelta(days=5)
            # set giveaway to expired if not found in the last 1-5 days according to supplier frequency
            if parse_datetime(fil['created_at']) < NOW - time_delta:
                for giveaway in giveaways:
                    if giveaway['supplier'] == fil['supplier']:
                        expired.append(fil)
                        expired_ids.append(fil['id'])
                        break

    # remove already active giveaways
    not_expired_giveaways = api.get_giveaways(
        status=[Giveaway.Status.PUBLISHED, Giveaway.Status.CANCELED,
                Giveaway.Status.QUEUED, Giveaway.Status.CREATED],
        limit=1000,
        order_by='-created_at',
    )

    for giveaway in list(giveaways):
        for active in not_expired_giveaways:
            if giveaway['supplier'] == active['supplier'] and (giveaway['url'] == active['url'] or giveaway['title'] == active['title']):
                giveaways.remove(giveaway)
                break

    return giveaways, expired


def get_msrps(giveaways):
    traceback_info = []
    try:
        titles = list(map(lambda x: str(x['title']), giveaways))
        prices = is_there_any_deal.get_prices(titles)
        for giveaway in list(giveaways):
            if 'msrp' in giveaway:
                continue
            for item in prices:
                if giveaway['title'] == item['title']:
                    giveaway['msrp'] = item['price']
    except Exception:
        traceback_info = traceback.format_exc()
    return giveaways, traceback_info


def get_steam_grid_db(giveaways):
    traceback_info = []
    try:
        titles = list(map(lambda x: str(x['title']), giveaways))
        grids = steam_grid_db.get_grids(titles)
        for index, giveaway in enumerate(list(giveaways)):
            giveaway['steam_grid_db_image'] = grids[index]
    except Exception:
        traceback_info = traceback.format_exc()
    return giveaways, traceback_info


def do_get_giveaways(suppliers):
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.stdout.flush()

    # run suppliers in parallel only if they have the same order
    suppliers_chunks = {}
    for supplier in suppliers:
        if supplier['order'] in suppliers_chunks:
            suppliers_chunks[supplier['order']].append(supplier)
        else:
            suppliers_chunks[supplier['order']] = [supplier]

    giveaways = []
    traceback_infos = []
    max_threads = 2
    threads = min(max_threads, len(suppliers))
    for order in suppliers_chunks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = []
            for supplier in suppliers_chunks[order]:
                futures.append(executor.submit(
                    get_giveaways, supplier=supplier))
            for future in concurrent.futures.as_completed(futures):
                giveaways += future.result()[0]
                traceback_infos.append(future.result()[1])
    return giveaways, traceback_infos


def save_giveaways(giveaways=[], expired=[]):
    traceback_infos = []
    giveaways_count_by_supplier = {}
    # TODO: bulk create?
    for giveaway in giveaways:
        supplier = giveaway['supplier']

        # skip review for specific suppliers and/or giveaway types
        skip_review = False
        if supplier == 'amazon' and giveaway['type'] == Giveaway.Type.LOOT:
            skip_review = True
        elif supplier == 'itch_io':
            skip_review = True
        elif supplier == 'is_there_any_deal' and giveaway['platforms'] is not None and 'itch_io' in giveaway['platforms']:
            skip_review = True
        if skip_review:
            giveaway['status'] = Giveaway.Status.QUEUED
            giveaway['publish_to_socials'] = False

        try:
            api.create_giveaway(giveaway=giveaway)
            if supplier in giveaways_count_by_supplier:
                giveaways_count_by_supplier[supplier] += 1
            else:
                giveaways_count_by_supplier[supplier] = 1
        except Exception:
            traceback_infos.append(traceback.format_exc())

    for supplier, count in giveaways_count_by_supplier.items():
        print(
            f"{supplier}: {count} giveaways found in {SCRAPE_TIME_BY_SUPPLIER[supplier]} seconds")
    sys.stdout.flush()

    if len(expired):
        # TODO: bulk update?
        for exp in expired:
            try:
                exp['status'] = Giveaway.Status.EXPIRED
                api.update_giveaway(exp)
            except Exception:
                traceback_infos.append(traceback.format_exc())

    return traceback_infos


def do_launch_scraper(suppliers=SUPPLIERS):
    giveaways_traceback_infos = []
    msrp_traceback_infos = []
    steam_grid_db_traceback_infos = []
    database_traceback_infos = []
    expired = []

    giveaways, giveaways_traceback_infos = do_get_giveaways(suppliers)
    giveaways, expired = mark_as_expired(giveaways)
    giveaways, msrp_traceback_infos = get_msrps(giveaways)
    giveaways, steam_grid_db_traceback_infos = get_steam_grid_db(giveaways)
    database_traceback_infos = save_giveaways(giveaways, expired)
    return giveaways_traceback_infos, msrp_traceback_infos, steam_grid_db_traceback_infos, database_traceback_infos
