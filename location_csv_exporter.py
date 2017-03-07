import csv
import os
import pickle

from utils import grab_access_token, get_all_locations, get_location_by_uuid


def cached_get_all_locations(access_token):
    if os.path.isfile('./out/all_locations_uuid.pickle'):
        with open('./out/all_locations_uuid.pickle') as f:
            return pickle.load(f)

    all_locations_uuid = get_all_locations(access_token)
    with open('./out/all_locations_uuid.pickle', 'w') as f:
        pickle.dump(all_locations_uuid, f)

    return all_locations_uuid


if __name__ == "__main__":
    access_token = grab_access_token()

    all_locations_uuid = cached_get_all_locations(access_token)

    locations_info = []
    for location_uuid in all_locations_uuid:
        locations_info.append(get_location_by_uuid(location_uuid, access_token))

    header_row = ["business name", "telephone", "email", "website", "facebook", "twitter", "location type"]

    location_rows = [[location[header] for header in header_row] for location in locations_info]

    try:
        os.makedirs('out')
    except OSError:
        if not os.path.isdir('out'):
            raise

    with open('./out/locations.csv', 'wb') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header_row)
        writer.writerows(location_rows)
