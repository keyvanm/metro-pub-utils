import os
import pickle

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


def cached_get_all_locations(access_token):
    if os.path.isfile('./out/all_locations_uuid.pickle'):
        with open('./out/all_locations_uuid.pickle') as f:
            return pickle.load(f)

    all_locations_uuid = get_all_locations(access_token)
    with open('./out/all_locations_uuid.pickle', 'w') as f:
        pickle.dump(all_locations_uuid, f)

    return all_locations_uuid


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
    return r.json()


def add_location_types_from_tags(location, access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    location_tags_request_url = API_URL + "/locations/" + location['uuid'] + "/tags"
    r = requests.get(location_tags_request_url, headers=headers)
    location['location_types'] = [tag["title"] for tag in r.json()['items'] if tag['predicate'] == "describes"]
