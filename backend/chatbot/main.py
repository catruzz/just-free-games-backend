#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Application class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""

import copy
import html
import logging
import os
import random
import re
import signal
from typing import Optional, Union
import tweepy

from django.utils.dateparse import parse_datetime
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMedia, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    filters,
    MessageHandler,
)
load_dotenv()


import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway  # nopep8
from backend.api import api  # nopep8

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

DEVELOPER_CHAT_ID = os.environ.get('TELEGRAM_DEVELOPER_CHAT_ID')
DEBUG = os.environ.get('DEBUG') != 'False'
USE_IMAGE_MESSAGE = True

PLATFORMS = api.get_platforms()

# stages
FIRST, SECOND = range(2)

DEFAULT_GIVEAWAY = {
    "platforms": [],
    "type": Giveaway.Type.OTHER,
    "title": "",
    "description": "",
    "url": "",
    "supplier": None,
    "expiration_date": "",
    "msrp": "",
    "post_id": "admin",
    "post_url": "",
    "post_image": "",
    "steam_grid_db_image": "",
}
temp_giveaway = copy.deepcopy(DEFAULT_GIVEAWAY)

pause_publish = False
pause_review = False
left_to_review = 0

DEFAULT_EDITING = {
    "id": False,
    "title": False,
    "description": False,
    "url": False,
    "expiration_date": False,
    "source": False,
    "msrp": False,
    "post_image": False,
    "steam_grid_db_image": False,
}
editing = copy.deepcopy(DEFAULT_EDITING)


def reset_temp_giveaway():
    global temp_giveaway, DEFAULT_GIVEAWAY
    temp_giveaway = copy.deepcopy(DEFAULT_GIVEAWAY)


def reset_editing():
    global editing, DEFAULT_EDITING
    editing = copy.deepcopy(DEFAULT_EDITING)


def get_giveaway_text(giveaway):
    # platforms
    platforms = giveaway["platforms"]
    platform_titles = []
    for platform_id in platforms:
        platform = next(
            item for item in PLATFORMS if item['id'] == platform_id)
        platform_title = re.sub(r'[\s\.]', '', platform['title'])
        platform_titles.append(platform_title)
        platform_titles.sort()
    text = f'[#{" / #".join(platform_titles)}] ' if platforms else '[Other] '

    # type
    type_values = Giveaway.Type.values
    type_labels = Giveaway.Type.labels
    type_label = 'Other'
    for type_index, type_value in enumerate(type_values):
        if giveaway["type"] == type_value:
            type_label = type_labels[type_index]
    text += f'({type_label}) '

    # title
    text += f'{html.escape(giveaway["title"])}'

    # url
    if 'url' in giveaway and giveaway['url']:
        text += f'\n{giveaway["url"]}'
    # description
    if 'description' in giveaway and giveaway['description']:
        text += f'\n({giveaway["description"]})'
    # source
    if 'show_source' in giveaway and giveaway['show_source'] and giveaway["post_url"]:
        text += f'\nSource: {giveaway["post_url"]}'

    bottom_text = []
    # msrp
    if 'msrp' in giveaway and giveaway['msrp'] and giveaway['msrp'] != 'None':
        bottom_text.append(f'MSRP: $ {giveaway["msrp"]}')
    # expiration_date
    if 'expiration_date' in giveaway and giveaway['expiration_date'] and giveaway['expiration_date'] != 'None':
        try:
            bottom_text.append(
                f'EXP: {parse_datetime(giveaway["expiration_date"]).strftime("%b %d, %Y")}')
        except Exception as exception:
            print(exception)
    text += f'\n{" | ".join(bottom_text)}' if bottom_text else ''

    return text


def get_temp_giveaway_hashtags_text():
    global temp_giveaway
    hashtags = ['giveaways', 'free', 'freebies']
    if temp_giveaway["type"] is not None and temp_giveaway["type"] is not Giveaway.Type.OTHER:
        hashtags += [str(temp_giveaway["type"]).lower()]
    platforms = temp_giveaway["platforms"]
    if 'Indiegala' in platforms or 'itch.io' in platforms:
        hashtags += ['indiegames']
    elif 'Steam' in platforms:
        hashtags += ['steam', 'freesteamkeys', 'freesteamgames']
    return f'#{" #".join(hashtags)}'


def get_temp_giveaway():
    global temp_giveaway, left_to_review
    text = get_giveaway_text(giveaway=temp_giveaway)
    if 'post_title' in temp_giveaway and 'post_url' in temp_giveaway:
        text += f'\n======= SOURCE ========'
        text += f'\nID: {temp_giveaway["id"]}'
        text += f'\nStatus: {temp_giveaway["status"]}'
        text += f'\nLeft to review: {left_to_review}'

        text += f'\n\n{html.escape(temp_giveaway["post_title"])}'
        text += f'\n{temp_giveaway["post_url"]}'
    return text


def get_temp_giveaway_image(force_steam_grid_db_image=False, force_post_image=False) -> Optional[str]:
    global temp_giveaway
    if not force_post_image and 'steam_grid_db_image' in temp_giveaway and (temp_giveaway['steam_grid_db_image'] or force_steam_grid_db_image):
        return temp_giveaway["steam_grid_db_image"]
    if not force_steam_grid_db_image and 'post_image' in temp_giveaway and (temp_giveaway['post_image'] or force_post_image):
        return temp_giveaway["post_image"]
    return None


def printable_exception_error(exception: Exception = None, custom_message: str = ''):
    global temp_giveaway

    return \
        "🚨 ERROR! 🚨" + \
        "\n" + \
        str(exception) if exception is not None else custom_message


def temp_giveaway_new():
    global temp_giveaway
    return 'id' not in temp_giveaway


def temp_giveaway_already_reviewed():
    global temp_giveaway
    return 'status' in temp_giveaway and temp_giveaway['status'] not in [Giveaway.Status.CREATED, Giveaway.Status.QUEUED]


def cancel_or_reset_button_text():
    if temp_giveaway_new() or temp_giveaway_already_reviewed():
        return 'Ignore'
    else:
        return 'Cancel'


def publish_or_update_button_text():
    if temp_giveaway_already_reviewed():
        return 'Update'
    else:
        return 'Publish'


def start_keyboard():
    return [
        [
            InlineKeyboardButton('Edit', callback_data='edit-start')
        ],
        submit_buttons()
    ]


def submit_buttons():
    return [
        InlineKeyboardButton(cancel_or_reset_button_text(),
                             callback_data='cancel'),
        InlineKeyboardButton(publish_or_update_button_text(),
                             callback_data='add_to_queue_confirm')
    ]


async def send_message(
    text: str,
    # if photo is False, override USE_IMAGE_MESSAGE
    photo: Optional[Union[str, bool]] = None,
    update: Optional[Update] = None,
    context: Optional[ContextTypes.DEFAULT_TYPE] = None,
    reply_markup: Optional[InlineKeyboardMarkup] = None,
    parse_mode: Optional[str] = ParseMode.HTML,
    # if edit_media is True and photo is None, will edit the media of the message with the default photo
    edit_media: bool = False,
    disable_notification: bool = False
) -> None:
    photo = get_temp_giveaway_image() if photo != False else photo
    send_image = USE_IMAGE_MESSAGE and photo

    # if update is None, we're starting a new conversation
    if not update:
        # Send message with text and appended InlineKeyboard
        if send_image:
            await context.bot.send_photo(
                chat_id=DEVELOPER_CHAT_ID, photo=photo, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            await context.bot.send_message(
                chat_id=DEVELOPER_CHAT_ID, text=text, reply_markup=reply_markup, parse_mode=parse_mode, disable_notification=disable_notification)
    else:
        # Instead of sending a new message, edit the message that originated the CallbackQuery.
        # This gives the feeling of an interactive menu.
        query = update.callback_query

        if send_image:
            if query:
                if edit_media:
                    media = InputMedia(media=photo, media_type='photo',
                                       caption=text, parse_mode=parse_mode) if photo else None
                    await query.edit_message_media(media=media, reply_markup=reply_markup)
                else:
                    await query.edit_message_caption(caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                await update.message.reply_photo(photo=photo, caption=text, reply_markup=reply_markup, parse_mode=parse_mode)
        else:
            if query:
                if not query.message.photo:
                    await query.edit_message_text(
                        text=text, reply_markup=reply_markup, parse_mode=parse_mode)
                else:
                    # if it's a photo message but the image is not available anymore (they have been deleted by the user),
                    # fallback to sending a new message if we can't edit the message
                    await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=text, reply_markup=reply_markup, parse_mode=parse_mode)
            elif update.message:
                await update.message.reply_text(
                    text=text, reply_markup=reply_markup, parse_mode=parse_mode)


async def welcome(context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "=== The cake is a lie ==="
    await send_message(context=context, text=text, disable_notification=True, photo=False)


async def review(context: ContextTypes.DEFAULT_TYPE) -> None:
    global temp_giveaway, pause_review, left_to_review
    if not pause_review:
        rows = api.get_giveaways(
            status=Giveaway.Status.CREATED, order_by='created_at')
        if rows:
            left_to_review = len(rows)-1
            temp_giveaway = rows[0]
            text = get_temp_giveaway()
            reply_markup = InlineKeyboardMarkup(start_keyboard())
            pause_review = True
            await send_message(context=context, text=text, reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    global pause_review
    pause_review = True

    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    if query:
        await query.answer()
    else:
        reset_temp_giveaway()

    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
        [
            InlineKeyboardButton('Create New', callback_data='create_or_edit'),
            InlineKeyboardButton(
                'Edit Existing', callback_data='load_existing')
        ],
        [
            InlineKeyboardButton('View Logs', callback_data='logs'),
            InlineKeyboardButton('Restart!', callback_data='restart'),
            InlineKeyboardButton('Reboot!', callback_data='reboot')
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "Welcome to JFG Bot! What do you want to do?"
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    # Tell ConversationHandler that we're in state `FIRST` now
    return FIRST


async def create_or_edit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Create a new giveaway or edit the temp giveaway"""
    query = update.callback_query
    if query:
        await query.answer()
    else:
        reset_temp_giveaway()
    reply_markup = InlineKeyboardMarkup(start_keyboard())
    text = get_temp_giveaway()
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    return FIRST


async def load_existing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Load an existing giveaway"""
    query = update.callback_query
    await query.answer()
    text = "Type Giveaway ID:"
    keyboard = [
        [InlineKeyboardButton('Back', callback_data='start')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['id'] = True
    return FIRST


async def edit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global temp_giveaway, pause_publish
    """Show editable fields"""

    """Get previous match, if any, and replace it to temp_giveaway"""
    if context.match and len(context.match.groups()) == 2:
        key, value = context.match.group(1, 2)
        if key == 'source' and editing['source']:
            temp_giveaway['show_source'] = not temp_giveaway['show_source']
        elif key == 'expiration' and editing['expiration_date']:
            temp_giveaway['expiration_date'] = None if value == "" else value
        else:
            temp_giveaway[key] = value
    elif update.message and update.message.text:
        # editing id means we are loading an existing giveaway from DB
        if editing['id']:
            # stop publishing process in case we want to change an enqueued giveaway
            pause_publish = True
            rows = api.get_giveaways(id=update.message.text, limit=1)
            if rows:
                temp_giveaway = rows[0]
        elif editing['title']:
            temp_giveaway['title'] = "" if update.message.text == "" else update.message.text
        elif editing['description']:
            temp_giveaway['description'] = "" if update.message.text == "" else update.message.text
        elif editing['url']:
            temp_giveaway['url'] = "" if update.message.text == "" else update.message.text
        elif editing['msrp']:
            temp_giveaway['msrp'] = "" if update.message.text == "" else update.message.text
        elif editing['expiration_date']:
            temp_giveaway['expiration_date'] = "" if update.message.text == "" else update.message.text
            # set time to 23:59:59 if no time was provided
            if len(temp_giveaway['expiration_date'].split(' ')) == 1:
                temp_giveaway['expiration_date'] += ' 23:59:59'
        elif editing['post_image']:
            temp_giveaway['post_image'] = "" if update.message.text == "" else update.message.text
        elif editing['steam_grid_db_image']:
            temp_giveaway['steam_grid_db_image'] = "" if update.message.text == "" else update.message.text

    reset_editing()

    query = update.callback_query
    if query:
        await query.answer()
    text = get_temp_giveaway()

    keyboard = [
        [
            InlineKeyboardButton('Platforms', callback_data='edit-platforms'),
            InlineKeyboardButton('Type', callback_data='edit-type'),
            InlineKeyboardButton('Title', callback_data='edit-title'),
        ],
        [
            InlineKeyboardButton('URL', callback_data='edit-url'),
            InlineKeyboardButton(
                'Description', callback_data='edit-description'),
            InlineKeyboardButton(
                'Source', callback_data='edit-source'),
        ],
        [
            InlineKeyboardButton(
                'Expiration Date', callback_data='edit-expiration'),
            InlineKeyboardButton(
                'MSRP', callback_data='edit-msrp'),
            InlineKeyboardButton('Image', callback_data='edit-image'),
            InlineKeyboardButton('Status', callback_data='edit-status'),
        ],
        submit_buttons()

    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    """query is None if previous step was free text input"""
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup, edit_media=True)

    return FIRST


async def edit_platforms(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global temp_giveaway
    """Show available platforms"""

    """Get previous match, if any, and replace it to temp_giveaway"""
    if context.match and len(context.match.groups()) == 1 and context.match.group(1) != '':
        platform = context.match.group(1)
        if platform in temp_giveaway['platforms']:
            temp_giveaway['platforms'].remove(platform)
        else:
            temp_giveaway['platforms'].append(platform)

    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Choose platforms:"

    keyboard = []
    row = []
    button_index = 0
    for platform in PLATFORMS:
        check_or_cross = '✅' if platform['id'] in temp_giveaway['platforms'] else '❌'
        button_text = f"{check_or_cross} {platform['title']}"
        button_callback = 'edit-platforms-' + platform['id']
        button = InlineKeyboardButton(
            button_text, callback_data=button_callback)

        if button_index == 0:
            keyboard.append(row)
        row.append(button)
        button_index += 1
        if button_index == 3:
            button_index = 0
            row = []

    keyboard.append([InlineKeyboardButton(
        'Back', callback_data='create_or_edit')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    return FIRST


async def edit_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available types"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Choose type:"
    type_values = Giveaway.Type.values
    type_labels = Giveaway.Type.labels

    keyboard = []
    row = []
    button_index = 0
    for type_index, type_value in enumerate(type_values):
        button_callback = 'edit-type-' + type_value
        button = InlineKeyboardButton(
            str(type_labels[type_index]), callback_data=button_callback)

        if button_index == 0:
            keyboard.append(row)
        row.append(button)
        button_index += 1
        if button_index == 3:
            button_index = 0
            row = []

    keyboard.append([InlineKeyboardButton(
        'Back', callback_data='create_or_edit')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    return FIRST


async def edit_title(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new title"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Type title:"
    keyboard = [
        [InlineKeyboardButton('Blank Title',
                              callback_data='edit-title-')],
        [InlineKeyboardButton('Back', callback_data='create_or_edit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['title'] = True
    return FIRST


async def edit_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new description"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Type description:"
    keyboard = [
        [InlineKeyboardButton('Blank Description',
                              callback_data='edit-description-')],
        [InlineKeyboardButton('Back', callback_data='create_or_edit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['description'] = True
    return FIRST


async def edit_source(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global temp_giveaway
    """Choose wether to show source or not"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Show source?"
    button_text = '✅ Yes, show source' if temp_giveaway[
        'show_source'] == False else '❌ No, hide source'
    keyboard = [
        [
            InlineKeyboardButton(button_text, callback_data='edit-source-'),
        ],
        [
            InlineKeyboardButton('Back', callback_data='create_or_edit'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['source'] = True
    return FIRST


async def edit_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new URL"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Type URL:"
    keyboard = [
        [InlineKeyboardButton('Blank URL',
                              callback_data='edit-url-')],
        [InlineKeyboardButton('Back', callback_data='create_or_edit'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['url'] = True
    return FIRST


async def edit_expiration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new expiration date"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Type expiration date (YYYY-MM-DD):"
    keyboard = [
        [InlineKeyboardButton('Blank Expiration Date',
                              callback_data='edit-expiration-')],
        [InlineKeyboardButton('Back', callback_data='create_or_edit'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['expiration_date'] = True
    return FIRST


async def edit_msrp(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new MSRP"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Type MSRP:"
    keyboard = [
        [InlineKeyboardButton('Blank MSRP',
                              callback_data='edit-msrp-')],
        [InlineKeyboardButton('Back', callback_data='create_or_edit'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    editing['msrp'] = True
    return FIRST


async def edit_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """List images"""
    query = update.callback_query
    await query.answer()
    text = "Steam Grid DB Image: "
    if temp_giveaway['steam_grid_db_image'] != '':
        text += temp_giveaway['steam_grid_db_image']
    else:
        text += "NONE"
    text += "\nPost Image: "
    if temp_giveaway['post_image'] != '':
        text += temp_giveaway['post_image']
    else:
        text += "NONE"

    keyboard = [
        [
            InlineKeyboardButton('Edit Steam Grid DB Image',
                                 callback_data='edit-steam_grid_db_image'),
            InlineKeyboardButton('Edit Post Image',
                                 callback_data='edit-post_image')
        ],
        [InlineKeyboardButton('Back', callback_data='create_or_edit')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup, edit_media=True)

    return FIRST


async def edit_steam_grid_db_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new Steam Grid DB Image"""
    query = update.callback_query
    await query.answer()
    text = "Steam Grid DB Image: "
    if temp_giveaway['steam_grid_db_image'] != '':
        text += temp_giveaway['steam_grid_db_image']
    else:
        text += "NONE"
    text += "\n\nType Steam Grid DB Image URL:"

    keyboard = [
        [InlineKeyboardButton('Blank Steam Grid DB Image',
                              callback_data='edit-steam_grid_db_image-')],
        [InlineKeyboardButton('Back', callback_data='edit-image'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, photo=get_temp_giveaway_image(force_steam_grid_db_image=True), reply_markup=reply_markup, edit_media=True)

    editing['steam_grid_db_image'] = True
    return FIRST


async def edit_post_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Ask for the new Post Image"""
    query = update.callback_query
    await query.answer()
    text = "Post Image: "
    if temp_giveaway['post_image'] != '':
        text += temp_giveaway['post_image']
    else:
        text += "NONE"
    text += "\n\nType Post Image URL:"

    keyboard = [
        [InlineKeyboardButton('Blank Post Image',
                              callback_data='edit-post_image-')],
        [InlineKeyboardButton('Back', callback_data='edit-image'),]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, photo=get_temp_giveaway_image(force_post_image=True), reply_markup=reply_markup, edit_media=True)

    editing['post_image'] = True
    return FIRST


async def edit_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show available statuses"""
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()+"\n\n"+"Choose status:"
    status_values = Giveaway.Status.values
    status_labels = Giveaway.Status.labels

    keyboard = []
    row = []
    button_index = 0
    for status_index, status_value in enumerate(status_values):
        button_callback = 'edit-status-' + status_value
        button = InlineKeyboardButton(
            str(status_labels[status_index]), callback_data=button_callback)

        if button_index == 0:
            keyboard.append(row)
        row.append(button)
        button_index += 1
        if button_index == 3:
            button_index = 0
            row = []

    keyboard.append([InlineKeyboardButton(
        'Back', callback_data='create_or_edit')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    return FIRST


async def add_to_queue_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    text = get_temp_giveaway()

    keyboard = [
        [
            InlineKeyboardButton(
                'Only on Website', callback_data='send-website'),
            InlineKeyboardButton('Everywhere', callback_data='send-everywhere')
        ],
        [
            InlineKeyboardButton('Back', callback_data='create_or_edit'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await send_message(update=update, context=context, text=text, reply_markup=reply_markup)

    # Transfer to conversation state `SECOND`
    return SECOND


async def add_to_queue(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    global temp_giveaway, pause_review, pause_publish

    query = update.callback_query
    await query.answer()

    if temp_giveaway_already_reviewed():
        text = f"✅ Updated! ✅"+"\n"+get_temp_giveaway()
    else:
        publish_to = None
        if context.match and len(context.match.groups()) == 1 and context.match.group(1) != '':
            publish_to = context.match.group(1)

        if publish_to == 'website':
            temp_giveaway['publish_to_socials'] = False
        else:
            temp_giveaway['publish_to_socials'] = True

        temp_giveaway['status'] = Giveaway.Status.QUEUED

        publish_to_text = f"on {publish_to}" if publish_to == 'website' else f"{publish_to}"
        text = f"✅ Published {publish_to_text}! ✅"+"\n"+get_temp_giveaway()

    # giveaway created from scratch
    if temp_giveaway_new():
        api.create_giveaway(giveaway=temp_giveaway)
    # else giveaway read from DB
    else:
        api.update_giveaway(giveaway=temp_giveaway)

    await send_message(update=update, context=context, text=text)

    pause_publish = False
    pause_review = False
    await review(context)
    return ConversationHandler.END


async def publish(context: ContextTypes.DEFAULT_TYPE) -> None:
    # do NOT use global temp_giveaway because this method runs in parallel with the others
    # and may overwrite the variable while reviewing giveaways

    if pause_publish:
        return

    # telegram settings
    chat_id = os.environ.get('TELEGRAM_CHANNEL_CHAT_ID')
    if DEBUG:
        chat_id = os.environ.get('TELEGRAM_TEST_CHANNEL_CHAT_ID')

    # twitter settings
    if not DEBUG:
        consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
        consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
        access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

        client = tweepy.Client(
            consumer_key=consumer_key, consumer_secret=consumer_secret,
            access_token=access_token, access_token_secret=access_token_secret
        )

    rows = api.get_giveaways(status=Giveaway.Status.QUEUED)
    for row in rows:
        giveaway_text = get_giveaway_text(giveaway=row)

        # prevent sending of empty title or url
        if row['title'] == '' or row['url'] == '':
            text = f"Blocked sending of invalid giveaway"+"\n"+giveaway_text
            await error_handler(update=None, context=context, custom_message=text)
            # save giveaway
            row['status'] = Giveaway.Status.CANCELED
            api.update_giveaway(giveaway=row)
            continue

        # set status to PUBLISHED only if it's enqueued
        if row['status'] == Giveaway.Status.QUEUED:
            row['status'] = Giveaway.Status.PUBLISHED
        # update the giveaway on DB before sending the message to the channels
        # to avoid sending the same giveaway multiple times in case of social media errors
        api.update_giveaway(giveaway=row)

        # skip if it has to be published only on website
        if row['publish_to_socials'] == True:

            # telegram
            await context.bot.send_message(chat_id=chat_id,
                                           text=giveaway_text,
                                           parse_mode=ParseMode.HTML,
                                           disable_web_page_preview=False)

            # twitter
            if not DEBUG:
                text = giveaway_text + '\n\n' + get_temp_giveaway_hashtags_text()
                client.create_tweet(text=text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over"""
    global temp_giveaway, pause_review, pause_publish
    query = update.callback_query
    await query.answer()

    # if temp_giveaway is new or already reviewed, don't update its status, just ignore it
    if temp_giveaway_new() or temp_giveaway_already_reviewed():
        text = "❌ Ignored! ❌"+"\n"+get_temp_giveaway()
    else:
        temp_giveaway['status'] = Giveaway.Status.CANCELED
        api.update_giveaway(giveaway=temp_giveaway)
        text = "❌ Canceled! ❌"+"\n"+get_temp_giveaway()

    await send_message(update=update, context=context, text=text)

    pause_publish = False
    pause_review = False
    await review(context)
    return ConversationHandler.END


async def still_alive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    texts = [
        'And believe me I am still alive',
        'I\'m doing Science and I\'m Still alive',
        'I feel FANTASTIC and I\'m Still alive',
        'While you\'re dying I\'ll be Still alive',
        'And when you\'re dead I will be Still alive',
    ]
    recipient = update.effective_chat.id
    text = random.choice(texts)
    if int(recipient) != int(DEVELOPER_CHAT_ID):
        text += \
            "\n\n" + \
            f"Unknown input received:" + \
            "\n" + \
            f"message: {str(update.message)}" + \
            "\n" + \
            f"user: {str(update.message.from_user)}" if update.message is not None else ''
    await send_message(context=context, text=random.choice(texts), photo=False)
    return ConversationHandler.END


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    recipient = update.effective_chat.id
    text = "Sorry, I didn't understand that command"
    if int(recipient) != int(DEVELOPER_CHAT_ID):
        text += \
            "\n\n" + \
            f"Unknown command received:" + \
            "\n" + \
            f"message: {str(update.message)}" + \
            "\n" + \
            f"user: {str(update.message.from_user)}" if update.message is not None else ''

    await send_message(context=context, text=text, photo=False)
    return ConversationHandler.END


async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE, disable_notification=False) -> int:
    global pause_publish, pause_review
    """Send logs file."""
    text = "📂 Saving logs... 📂"
    await send_message(context=context, text=text, photo=False, disable_notification=disable_notification)
    os.system('pm2 logs --lines 100 --nostream > logs/logs.txt')
    with open('logs/logs.txt', 'rb') as file:
        await context.bot.send_document(chat_id=DEVELOPER_CHAT_ID, document=file, disable_notification=disable_notification)

    pause_publish = False
    pause_review = False
    await review(context)
    return ConversationHandler.END


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global pause_publish, pause_review
    text = "🔄 Restarting all processes... 🔄"
    await send_message(context=context, text=text, photo=False)
    os.system('pm2 restart all')

    pause_publish = False
    pause_review = False
    return ConversationHandler.END


async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global pause_publish, pause_review
    text = "🔄 Rebooting server... 🔄"
    await send_message(context=context, text=text, photo=False)
    os.system('reboot')

    pause_publish = False
    pause_review = False
    return ConversationHandler.END


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE, custom_message: str = '') -> int:
    """Log the error and send a telegram message to notify the developer."""
    global pause_publish, pause_review
    # Log the error before we do anything else, so we can see it even if something breaks.
    logger.error("Exception while handling an update:", exc_info=context.error)
    if custom_message != '':
        text = printable_exception_error(custom_message)
    else:
        text = printable_exception_error(exception=context.error)

    pause_publish = False
    pause_review = False

    # Finally, send the message, without notification
    await send_message(context=context, text=text, disable_notification=True, photo=False)
    return logs(update, context, disable_notification=True)


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    if DEBUG:
        TOKEN = os.environ.get('TELEGRAM_TEST_BOT_TOKEN')
    else:
        TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    application = Application.builder().token(TOKEN).build()

    # Get job queue
    job_queue = application.job_queue

    # Send welcome message
    job_queue.run_once(welcome, 0)
    # Run reviewer every 5 minutes
    job_queue.run_repeating(review, interval=300, first=1)
    # Run publisher every 1 minute
    job_queue.run_repeating(publish, interval=60, first=1)

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(edit_start, pattern='^edit-start$'),
            CallbackQueryHandler(cancel, pattern='^cancel$'),
            CallbackQueryHandler(add_to_queue_confirm,
                                 pattern='^add_to_queue_confirm$'),
        ],
        states={
            FIRST: [
                CallbackQueryHandler(start, pattern='^start$'),
                CallbackQueryHandler(logs, pattern='^logs$'),
                CallbackQueryHandler(restart, pattern='^restart$'),
                CallbackQueryHandler(reboot, pattern='^reboot$'),
                CallbackQueryHandler(
                    create_or_edit, pattern='^create_or_edit$'),
                CallbackQueryHandler(load_existing, pattern='^load_existing$'),
                CallbackQueryHandler(edit_start, pattern='^edit-start$'),
                CallbackQueryHandler(cancel, pattern='^cancel$'),
                CallbackQueryHandler(
                    edit_platforms, pattern='^edit-platforms-?(.*)'),
                CallbackQueryHandler(edit_type, pattern='^edit-type$'),
                CallbackQueryHandler(edit_title, pattern='^edit-title$'),
                CallbackQueryHandler(
                    edit_description, pattern='^edit-description$'),
                CallbackQueryHandler(edit_source, pattern='^edit-source$'),
                CallbackQueryHandler(edit_url, pattern='^edit-url$'),
                CallbackQueryHandler(
                    edit_expiration, pattern='^edit-expiration$'),
                CallbackQueryHandler(edit_msrp, pattern='^edit-msrp$'),
                CallbackQueryHandler(edit_image, pattern='^edit-image$'),
                CallbackQueryHandler(edit_steam_grid_db_image,
                                     pattern='^edit-steam_grid_db_image$'),
                CallbackQueryHandler(
                    edit_post_image, pattern='^edit-post_image$'),
                CallbackQueryHandler(edit_status, pattern='^edit-status$'),
                CallbackQueryHandler(edit_start, pattern='^edit-(.*)-(.*)'),
                # free text input
                MessageHandler(filters.TEXT & ~filters.COMMAND, edit_start),
                CallbackQueryHandler(add_to_queue_confirm,
                                     pattern='^add_to_queue_confirm$'),
            ],
            SECOND: [
                CallbackQueryHandler(
                    create_or_edit, pattern='^create_or_edit$'),
                CallbackQueryHandler(add_to_queue, pattern='^send-(.*)$'),
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, still_alive))
    # add the error handler
    application.add_error_handler(error_handler)

    # TODO: use webhook in production ENV
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)
