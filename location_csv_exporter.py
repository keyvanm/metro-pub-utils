import csv
import os
import pickle

from requests.exceptions import ConnectionError

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

    print "Access Token obtained"

    all_locations_uuid = cached_get_all_locations(access_token)

    print "All location UUIDs obtained"

    header_row = ["business name", "telephone", "email", "website", "facebook", "twitter", "location type"]

    try:
        os.makedirs('out')
    except OSError:
        if not os.path.isdir('out'):
            raise

    with open('./out/locations.csv', 'wb') as csv_file:
        print "Starting to create CSV"
        writer = csv.writer(csv_file)
        writer.writerow(header_row)
        failed_location_uuids = []
        for i, location_uuid in enumerate(all_locations_uuid):
            if (i + 1) % 10 == 0:
                print "Progress: {i}/{length}".format(i=i + 1, length=len(all_locations_uuid))
            try:
                location = get_location_by_uuid(location_uuid, access_token)
                writer.writerow([location[header] for header in header_row])
            except ConnectionError as e:
                print e.message
                failed_location_uuids.append(location_uuid)

    print "Failed locations: ", failed_location_uuids
