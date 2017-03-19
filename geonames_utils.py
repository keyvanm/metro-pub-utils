import os

import requests

GEONAME_USER = os.environ['GEONAMES_USERNAME']

_GEONAMES_CACHE = {}


def get_one_geoname(geoname_id):
    """Get geoname info from http://api.geonames.org/"""
    geoname = _GEONAMES_CACHE.get(geoname_id)
    if geoname is None:
        geoname_url = 'http://api.geonames.org/getJSON?geonameId={}&username={}&style=full'.format(geoname_id,
                                                                                                   GEONAME_USER)
        geoname = requests.get(geoname_url).json()
        _GEONAMES_CACHE[geoname_id] = geoname
    return geoname


def add_geoname_data(location):
    """Merge some data from the geoname into the location dict"""
    geoname_id = location['geoname_id']
    if geoname_id is None:
        geoname = {}
    else:
        geoname = get_one_geoname(geoname_id)
    if geoname.get('name'):
        location['geoname_name'] = geoname.get('name')
    elif geoname.get('asciiName'):
        location['geoname_name'] = geoname.get('asciiName')
    else:
        location['geoname_name'] = 'None'
    if geoname.get('adminCode1'):
        location['location_state'] = geoname.get('adminCode1')
    return location
