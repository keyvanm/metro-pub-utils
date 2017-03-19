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


def get_all_locations(access_token=None, debug=False):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    locations = []
    url = API_URL + "/locations?"
    query_params = "fields=uuid&rpp=100" if not debug else "fields=uuid&rpp=10"

    while query_params:
        r = requests.get(url + query_params, headers=headers)
        payload = r.json()
        locations.extend([item[0] for item in payload['items']])
        query_params = payload.get('next') if not debug else None

    return locations


def cached_get_all_locations(access_token, debug=False):
    filepath = './out/all_locations_uuid_{iid}.pickle'.format(iid=os.environ['INSTANCE_ID'])
    if os.path.isfile(filepath):
        with open(filepath) as f:
            return pickle.load(f) if not debug else pickle.load(f)[:10]

    all_locations_uuid = get_all_locations(access_token, debug)
    if not debug:
        with open(filepath, 'w') as f:
            pickle.dump(all_locations_uuid, f)

    return all_locations_uuid


def encode_if_possible(value):
    if value is None:
        return value
    try:
        return str(value)
    except UnicodeEncodeError:
        return value.encode('utf-8')


def get_location_by_uuid(uuid_str, access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    location_request_url = API_URL + "/locations/" + uuid_str
    r = requests.get(location_request_url, headers=headers)
    return r.json()


def get_tags_for_item(item_url, access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    tags_url = item_url + "/tags"
    return requests.get(tags_url, headers=headers).json()['items']


def add_location_types_from_tags(location, access_token=None):
    if not access_token:
        access_token = grab_access_token()

    location_request_url = API_URL + "/locations/" + location['uuid']
    tags = get_tags_for_item(location_request_url, access_token)
    location['location_types'] = [tag["title"] for tag in tags if tag['predicate'] == "describes"]


def get_tag_category_titles(tag, access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    categories_url = tag['url'] + '/categories?fields=title'
    items = requests.get(categories_url, headers=headers).json()['items']
    return [item[0] for item in items]


def get_category(category_url, access_token=None):
    if not access_token:
        access_token = grab_access_token()
    headers = {'Authorization': "Bearer " + access_token}

    return requests.get(category_url, headers=headers).json()


def add_location_guide_tags(location, access_token=None):
    if not access_token:
        access_token = grab_access_token()

    location_url = API_URL + "/locations/" + location['uuid']
    tags = get_tags_for_item(location_url, access_token)
    location['tags'] = [tag['title'] for tag in tags]

    categories_set = set()
    for tag in tags:
        tag_categories = get_tag_category_titles(tag, access_token)
        categories_set.update(tag_categories)

    location['categories'] = categories_set
