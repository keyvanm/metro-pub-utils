import os
import requests

ROOT_URL = os.environ['ROOT_URL']
API_URL = ROOT_URL + os.environ['INSTANCE_ID']
TOKEN_URL = os.environ['TOKEN_URL']


def grab_access_token():
    data = {
        'api_secret': os.environ['API_SECRET'],
        'api_key': os.environ['API_KEY'],
        'grant_type': 'client_credentials'
    }
    r = requests.post(TOKEN_URL, data=data)
    return r.json()['access_token']


def get_all_locations(access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    locations = []
    url = API_URL + "/locations?"
    query_params = "fields=uuid&rpp=100"

    while query_params:
        r = requests.get(url + query_params, headers=headers)
        payload = r.json()
        locations.extend([item[0] for item in payload['items']])
        query_params = payload.get('next')

    return locations


def encode_if_possible(unicode_string):
    if unicode_string is None:
        return unicode_string
    return unicode_string.encode('utf-8')


def get_location_by_uuid(uuid_str, access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    location_request_url = API_URL + "/locations/" + uuid_str
    r = requests.get(location_request_url, headers=headers)
    location_info = r.json()
    # r = requests.get(location_request_url + "/tags", headers=headers)
    # location_types = [tag["title"] for tag in r.json()['items']]

    return {
        "business name": encode_if_possible(location_info['title']),
        "telephone": encode_if_possible(location_info['phone']),
        "email": encode_if_possible(location_info['email']),
        "website": encode_if_possible(location_info['website']),
        "facebook": encode_if_possible(location_info['fb_url']),
        "twitter": encode_if_possible(location_info['twitter_username']),
        "location type": encode_if_possible(" / ".join(location_info['location_types']))
    }
