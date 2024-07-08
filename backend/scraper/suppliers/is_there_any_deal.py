import traceback
from backend.api import is_there_any_deal
from backend.scraper.utils import lib


def get_giveaways(supplier_id):
    giveaways = []

    try:
        deals = is_there_any_deal.get_deals()
        for item in deals:
            title = item['title']
            deal = item['deal']
            shop_name = deal['shop']['name']
            drms = list(map(lambda x: str(x['name']), deal['drm']))
            platform_text = ", ".join(drms) + f" {shop_name}"
            type_text = item['type'] or 'game'
            giveaway_platforms = lib.get_giveaway_platforms(platform_text)
            giveaway_type = lib.get_giveaway_type(type_text)
            giveaway_title = lib.get_giveaway_title(title)

            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': deal['url'],
                'description': '',
                'supplier': supplier_id,
                'show_source': True,
                'msrp': deal['regular']['amount'],
                'post_id': '',
                'post_title': title,
                # slug should be always present, but just in case
                'post_url': f"https://isthereanydeal.com/game/{item['slug']}/info/" if item['slug'] else deal['url'],
                'post_image': '',
            })
    except Exception:
        traceback.print_exc()

    return giveaways
