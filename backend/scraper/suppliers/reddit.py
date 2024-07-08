from dotenv import load_dotenv
from backend.scraper.utils import lib
import os
import praw
import re
import traceback
load_dotenv()


def parse_title(text):
    giveaway_platforms = ''
    giveaway_type = ''
    giveaway_title = ''

    try:
        searchObj = re.search(r'(\[(.*?)\])*\s*(\((.*?)\))*\s*(.*)', text)

        giveaway_platforms = str(searchObj.group(2))
        giveaway_type = str(searchObj.group(4))
        giveaway_title = str(searchObj.group(5))

        giveaway_platforms = lib.get_giveaway_platforms(giveaway_platforms)
        giveaway_title = lib.get_giveaway_title(giveaway_title)
        giveaway_type = lib.get_giveaway_type(giveaway_type)
        if giveaway_type == None:
            giveaway_type = lib.get_giveaway_type(giveaway_title)
    except Exception:
        traceback.print_exc()
        raise

    return giveaway_platforms, giveaway_type, giveaway_title


def get_giveaways(supplier_id):
    giveaways = []
    try:
        reddit = praw.Reddit(client_id=os.environ.get('REDDIT_CLIENT_ID'),
                             client_secret=os.environ.get(
                                 'REDDIT_CLIENT_SECRET'),
                             user_agent=os.environ.get('REDDIT_USER_AGENT'),
                             username=os.environ.get('REDDIT_USERNAME'),
                             password=os.environ.get('REDDIT_PASSWORD'))
        subreddit = reddit.subreddit('FreeGameFindings')
        new_subreddit = subreddit.new(limit=20)  # topic limit

        for submission in new_subreddit:
            # skip already expired giveaways
            link_flair_template_id = submission.link_flair_template_id if hasattr(
                submission, 'link_flair_template_id') else ''
            link_flair_text = submission.link_flair_text if hasattr(
                submission, 'link_flair_text') else ''
            if (link_flair_text is not None and 'Expired' in link_flair_text) or link_flair_template_id == '3f44a048-da47-11e3-8cba-12313d051ab0':
                continue
            # TODO: get the correct flair id for F2P giveaways
            if (link_flair_text is not None and 'F2P' in link_flair_text):
                continue

            giveaway = parse_title(str(submission.title))
            giveaway_platforms, giveaway_type, giveaway_title = giveaway
            giveaways.append({
                'platforms': giveaway_platforms,
                'type': giveaway_type,
                'title': giveaway_title,
                'url': submission.url,
                'description': '',
                'supplier': supplier_id,
                'show_source': True,
                'post_id': submission.id,
                'post_title': submission.title,
                'post_url': submission.shortlink,
                'post_image': '',
            })
    except Exception:
        traceback.print_exc()
        raise

    return giveaways
