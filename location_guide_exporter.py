import csv
import os

from requests.exceptions import ConnectionError

from utils import grab_access_token, get_location_by_uuid, cached_get_all_locations, encode_if_possible, \
    add_location_guide_tags


FILTER = '_Filter: Shop Type'


def process_location_for_csv_export(location):
    output = {}
    for k, v in location.items():
        if isinstance(v, list) or isinstance(v, set):
            v = " | ".join([unicode(i) for i in v])
        output[k] = encode_if_possible(v)
    return output


if __name__ == "__main__":
    access_token = grab_access_token()

    print "Access Token obtained"

    all_locations_uuid = cached_get_all_locations(access_token)

    print "All location UUIDs obtained ({})".format(len(all_locations_uuid))

    sample_uuid = all_locations_uuid[0]
    location = get_location_by_uuid(sample_uuid, access_token)
    add_location_guide_tags(location, access_token)

    header_row = location.keys()

    try:
        os.makedirs('out')
    except OSError:
        if not os.path.isdir('out'):
            raise

    with open('./out/location_guide_{iid}.csv'.format(iid=os.environ['INSTANCE_ID']), 'wb') as csv_file:
        print "Starting to create CSV"
        writer = csv.writer(csv_file)
        writer.writerow(header_row)
        failed_location_uuids = []
        for i, location_uuid in enumerate(all_locations_uuid):
            if (i + 1) % 10 == 0:
                print "Progress: {i}/{length}".format(i=i + 1, length=len(all_locations_uuid))
            try:
                location = get_location_by_uuid(location_uuid, access_token)
                add_location_guide_tags(location, access_token)
                if FILTER in location['categories']:
                    processed_location = process_location_for_csv_export(location)
                    writer.writerow([processed_location[header] for header in header_row])
            except ConnectionError as e:
                print e.message
                failed_location_uuids.append(location_uuid)

    print "Failed locations: ", failed_location_uuids
