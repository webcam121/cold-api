import requests
from datetime import datetime
from django.conf import settings

EXPERT_SENDER_API_KEY = settings.EXPERT_SENDER_API_KEY
EXPERT_SENDER_API_URL = settings.EXPERT_SENDER_API_URL


def add_subscriber_to_blacklist(email):
    requests.delete(f'{EXPERT_SENDER_API_URL}/v2/Api/Subscribers?apiKey={EXPERT_SENDER_API_KEY}&email={email}&addToBlacklist=true')
