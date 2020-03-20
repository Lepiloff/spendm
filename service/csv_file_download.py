import csv
import json

from rest_framework.exceptions import ParseError
from rest_framework.response import Response

from apps.vendors.models import Vendors, VendorContacts

jsonFilePath ='json_file_name.json'

def csv_file_parser(file):
    vendor_error = []
    email_error = []

    csv_fields = [
                  'Vendor',
                  'Country',
                  'NDA date',
                  'Primary Contact Name',
                  'Primary Contact Email',
                  'Secondary Contact Name',
                  'Secondary Contact Email',
                  'Modules'
                 ]
    modules_list = [
               "Sourcing",
               "SA",
               "SXM",
               "CLM",
               "ePRO",
               "I2P",
               "P2P",
               "SPT",
               "S2P",
               "AP",
               "TS",
               "SOW",
               "ICW"
               ]
    result_dict = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        # check the csv file header is equal for template
        if headers != csv_fields:
            raise ParseError('Wrong fields in csv file. Use our template.')
        for count, rows in enumerate(reader, 1):
            for key, value in rows.items():
                if not rows[key]:
                    if key == 'NDA date' or key == 'Secondary Contact Name' or key == 'Secondary Contact Email' \
                            or key == 'Modules':
                        pass
                    else:
                        raise ParseError('Missing value in file! Check the {} line field {}'.format(count, key))
                if key == 'Modules':
                    if value != '':
                        for v in value.split(','):
                            if v not in modules_list:
                                raise ParseError(
                                    'Check the Modules field value. Accepted value are: {}'.format(modules_list))

                if key == "Vendor":
                        vendor = Vendors.objects.filter(vendor_name=value).first()
                        if vendor:
                            vendor_error.append(['Error in row {}: '
                                                 'Vendor {} already exist. '
                                                 'Please correct the error and try again'.format(count, value)])
                if key == "Primary Contact Email" or key == "Secondary Contact Name":
                        email = VendorContacts.objects.filter(email=value).first()
                        if email:
                            email_error.append(['Error in row {}: '
                                                'Email {} already exist. '
                                                'Please correct the error and try again'.format(count, value)])

            result_dict.append(rows)
        if len(vendor_error) or len(email_error):
            raise ParseError(detail={'The file could not be uploaded': [vendor_error, email_error]})
        # Remove contact from result_dict wright it to intermediate_dict
        # and update result_dict['contacts'] as intermediate_dict
        # change keys to models field name format
        for vendor in result_dict:
            vendor.update(vendor_name=vendor.pop('Vendor', None),
                          country=vendor.pop('Country', None),
                          nda=vendor.pop('NDA date', None),)
            # Modules
            modules = (vendor.pop('Modules', None)).split(',')
            vendor_module_list = []
            for module in modules:
                vendor_module_list.append({'module': module})
            vendor['modules'] = vendor_module_list
            # Contact
            email = vendor.pop('Primary Contact Email', None)
            contact_name = vendor.pop('Primary Contact Name', None)
            s_email = vendor.pop('Secondary Contact Email', None)
            s_contact_name = vendor.pop('Secondary Contact Name', None)
            contact = [{'email': email, 'contact_name': contact_name, 'primary': True},
                       {'email': s_email, 'contact_name': s_contact_name, 'primary': False}]
            vendor['contacts'] = contact
    return result_dict
