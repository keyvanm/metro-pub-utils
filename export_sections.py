import csv
import os

from utils import grab_access_token, build_sections_tree, get_all_sections, get_all_tags, encode_if_possible


def write_tree_to_csv(tree, csv_writer, prething=""):
    if tree.value == "root":
        for child in tree.children:
            write_tree_to_csv(child, csv_writer)
    else:
        csv_writer.writerow([prething + tree.value])
        for child in tree.children:
            write_tree_to_csv(child, csv_writer, prething=prething + tree.value + "/")


if __name__ == "__main__":
    access_token = grab_access_token()

    print "Access Token obtained"

    tree = build_sections_tree(get_all_sections(access_token))

    print "Getting Sections"
    with open('./out/all_sections_{iid}.csv'.format(iid=os.environ['INSTANCE_ID']), 'wb') as csv_file:
        print "Starting to create CSV"
        writer = csv.writer(csv_file)
        write_tree_to_csv(tree, writer)

    print "Getting Tags"
    tag_fields = ['title']#, 'type']
    tags = get_all_tags(tag_fields, access_token)
    tags = [[encode_if_possible(item) for item in tag] for tag in tags]

    with open('./out/all_tags_{iid}.csv'.format(iid=os.environ['INSTANCE_ID']), 'wb') as csv_file:
        print "Starting to create CSV"
        writer = csv.writer(csv_file)
        # writer.writerow(tag_fields)
        writer.writerows(tags)

