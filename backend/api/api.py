from typing import List
from dotenv import load_dotenv
import os
import requests
load_dotenv()

import django  # nopep8
django.setup()  # nopep8
from backend.models import Giveaway  # nopep8

API_URL = 'http://127.0.0.1:8000/api/'
API_URL_GIVEAWAYS = f"{API_URL}giveaways/"
API_URL_PLATFORMS = f"{API_URL}platforms/"
API_URL_SUPPLIERS = f"{API_URL}suppliers/"


def get_auth_token():
    try:
        username = os.environ.get('TELEGRAM_BOT_API_USERNAME')
        password = os.environ.get('TELEGRAM_BOT_API_PASSWORD')
        response = requests.post(
            url=f"{API_URL}token-auth/",
            data={'username': username, 'password': password}
        )
        response.raise_for_status()
        return response.json()['token']
    except Exception as exception:
        print(exception)


API_TOKEN = get_auth_token()
HEADERS = {'Authorization': f'Token {API_TOKEN}'}


def get_giveaways(
        id: int = None,
        status: Giveaway.Status or List[Giveaway.Status] = [],
        supplier: str or List[str] = [],
        order_by: str = None,
        limit=None
):
    if type(status) != list:
        status = [status]
    if type(supplier) != list:
        supplier = [supplier]
    response = requests.get(
        url=API_URL_GIVEAWAYS,
        headers=HEADERS,
        params={
            'id': id,
            'status': status,
            'supplier': supplier,
            'order_by': order_by,
            'limit': limit
        }
    )
    response.raise_for_status()
    return response.json()


def create_giveaway(giveaway):
    response = requests.post(
        url=API_URL_GIVEAWAYS,
        headers=HEADERS,
        data=giveaway
    )
    response.raise_for_status()
    return response.json()


def update_giveaway(giveaway):
    response = requests.put(
        url=f"{API_URL_GIVEAWAYS}{str(giveaway['id'])}/",
        headers=HEADERS,
        data=giveaway
    )
    response.raise_for_status()
    return response.json()


def get_platforms(id=[]):
    if type(id) != list:
        id = [id]
    response = requests.get(
        url=API_URL_PLATFORMS,
        headers=HEADERS,
        params={'id': id}
    )
    response.raise_for_status()
    return response.json()


def get_suppliers(id=[]):
    if type(id) != list:
        id = [id]
    response = requests.get(
        url=API_URL_SUPPLIERS,
        headers=HEADERS,
        params={'enabled': True, 'id': id}
    )
    response.raise_for_status()
    return response.json()


def update_supplier(supplier):
    response = requests.put(
        url=f"{API_URL_SUPPLIERS}{str(supplier['id'])}/",
        headers=HEADERS,
        data=supplier
    )
    response.raise_for_status()
    return response.json()
