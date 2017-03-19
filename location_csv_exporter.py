import csv
import os

from requests.exceptions import ConnectionError

from utils import grab_access_token, get_location_by_uuid, cached_get_all_locations, encode_if_possible, \
    add_location_types_from_tags


def process_location_for_csv_export(location):
    return {
        "business name": encode_if_possible(location['title']),
        "telephone": encode_if_possible(location['phone']),
        "email": encode_if_possible(location['email']),
        "website": encode_if_possible(location['website']),
        "facebook": encode_if_possible(location['fb_url']),
        "twitter": encode_if_possible(location['twitter_username']),
        "location type": encode_if_possible(" | ".join(location['location_types']))
    }


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
                add_location_types_from_tags(location, access_token)
                processed_location = process_location_for_csv_export(location)
                writer.writerow([processed_location[header] for header in header_row])
            except ConnectionError as e:
                print e.message
                failed_location_uuids.append(location_uuid)

    print "Failed locations: ", failed_location_uuids
