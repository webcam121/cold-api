import json

import requests
from django.conf import settings

base_url = settings.FRONTEND_BASE_URL

if settings.ENVIRONMENT == 'production':
    api_key = ''


def create_referral_link(email):
    params = f'?utm_source=referral&utm_campaign={email}'
    return base_url + params


def shorten_url(url):
    req = requests.get(f'https://cutt.ly/api/api.php?key={api_key}&short={url}')
    data = json.loads(req.text)
    return data['url']['shortLink']
