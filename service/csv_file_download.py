import csv
import json

from apps.vendors.models import Vendors
from rest_framework.exceptions import ParseError


# def csv_file_parser(file):
#
#     with open(file) as csvfile:
#         reader = csv.DictReader(csvfile)
#         line_count = 1
#         result_dict = {}
#         for row in reader:
#             for key, value in row.items():
#                 if not value:
#                     raise ParseError('Missing value in file. Check the {} line'.format(line_count))
#             new = {line_count: row}
#             result_dict.update(new)
#             line_count += 1
#
#         return json.dumps(result_dict)


jsonFilePath ='json_file_name.json'

def csv_file_parser(file):
    result_dict = {}
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for count, rows in enumerate(reader, 1):
            for key, value in rows.items():
                if not rows[key] and key != 'NDA date':
                    raise ParseError('Missing value in file. Check the {} line'.format(count))
            result_dict[count] = rows

    # wright json file

    # with open(jsonFilePath, 'w') as jsonFile:
    #     jsonFile.write(json.dumps(result_dict, indent=4))

    return result_dict

def add_vendors_to_database_from_csv(data):
    # with open(storage, encoding='utf8') as file:
    all_of_vendors = json.dump(data)
    print(all_of_vendors)
    # for vendor in all_of_vendors:
    #     Vendors(
    #         vendor_name=vendor['Vendor'],
    #         country=vendor['Country']
    #     ).save()
