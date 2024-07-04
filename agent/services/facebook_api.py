import json
import re
import requests
from hashlib import sha256
from django.conf import settings

BASE_FB_ENDPOINT = 'https://graph.facebook.com/v16.0/{pixel_id}/events?access_token={api_key}'
IPHONE_USERAGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"


def fire_facebook_event(
        event_name,
        event_time,
        action_source,
        user_data=None,
        conversion_value=None,
        client_ip_address=None,
        client_user_agent=None,
        fbc=None,
        event_source_url=None,
):
    if client_user_agent:
        if is_ios_14_or_above(client_user_agent):
            client_user_agent = IPHONE_USERAGENT

    if settings.ENVIRONMENT != 'production':
        return 'test', client_user_agent
    try:
        conversion_endpoint = BASE_FB_ENDPOINT.format(
            pixel_id=settings.FB_CONVERSION_API_PIXEL_ID,
            api_key=settings.FB_CONVERSION_API_ACCESS_TOKEN
        )

        source_url = {'event_source_url': event_source_url} if event_source_url else {}
        ip_address = {'client_ip_address': client_ip_address} if client_ip_address else {}
        user_agent = {'client_user_agent': client_user_agent} if client_user_agent else {}
        custom_data = {'custom_data': {'value': conversion_value, 'currency': 'USD'}} \
            if conversion_value else {'custom_data': {'value': 60, 'currency': 'USD'}}

        ph = {'ph': sha256(user_data['phone_number'].encode('utf-8')).hexdigest()} if user_data.get('phone_number') else {}
        em = {'em': sha256(user_data['email'].encode('utf-8')).hexdigest()} if user_data.get('email') else {}
        fn = {'fn': sha256(user_data['first_name'].encode('utf-8')).hexdigest()} if user_data.get('first_name') else {}
        ln = {'ln': sha256(user_data['last_name'].encode('utf-8')).hexdigest()} if user_data.get('last_name') else {}
        fbclid = {'fbc': fbc} if fbc else {}
        params = {
            'data': [
                {
                    'event_name': event_name,
                    'event_time': event_time,
                    'action_source': action_source,
                    **source_url,
                    **custom_data,
                    'user_data': {
                        **ip_address,
                        **user_agent,
                        **fbclid,
                        **ph,
                        **em,
                        **fn,
                        **ln,
                        'external_id': sha256(user_data['id'].encode('utf-8')).hexdigest(),
                    }
                }
            ]
        }
        resp = requests.post(
            conversion_endpoint,
            data=json.dumps(params),
            headers={'Content-Type': 'application/json'}
        )
        print(resp.text, resp.status_code)
        return resp.text, client_user_agent
    except Exception as e:
        print(e)
        raise ValueError('Facebook event failed to fire')


def is_ios_14_or_above(user_agent):
    match = re.search(r'(iPhone|iPad); CPU (?:iPhone )?OS (\d+)', user_agent)
    if match:
        ios_version = int(match.group(2))
        if ios_version >= 14:
            return True
    return False

