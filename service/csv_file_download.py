import csv
import pandas as pd


from rest_framework.exceptions import ParseError

from apps.vendors.models import Vendors, VendorContacts, Rfis
from service.countries import COUNTRIES_LIST

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


def csv_file_parser(file):
    vendor_error = []
    email_error = []
    country_error = []
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

    result_dict = []
    with open(file, encoding='windows-1252') as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        # check the csv file header is equal for template
        if headers != csv_fields:
            raise ParseError('Wrong fields in csv file. Use our template.')


        # Check uniques vendor name and email in file without request to DB using pandas
        result_vendor_name_error = []
        result_vendor_email_error = []
        record = pd.read_csv(file, encoding='windows-1252')
        df = pd.DataFrame(data=record)
        vendor_name_error = {v: k + 1 for k, v in df.loc[df['Vendor'].duplicated() & df['Primary Contact Email'].notna(), 'Vendor'].items()}
        vendor_p_email_error = {v: k + 1 for k, v in df.loc[df['Primary Contact Email'].duplicated() & df['Primary Contact Email'].notna(), 'Primary Contact Email'].items()}
        vendor_s_email_error = {v: k + 1 for k, v in df.loc[df['Secondary Contact Email'].duplicated() & df['Secondary Contact Email'].notna(), 'Secondary Contact Email'].items()}
        # Create list of error
        if len(vendor_s_email_error):
            for k, v in vendor_s_email_error.items():
                result_vendor_email_error.append(['Error in row {}: '
                                                    'Email {} already exist. '
                                                    'Please correct the error and try again'.format(v, k)])
        if len(vendor_p_email_error):
            for k, v in vendor_p_email_error.items():
                result_vendor_email_error.append(['Error in row {}: '
                                                    'Email {} already exist. '
                                                    'Please correct the error and try again'.format(v, k)])
        if len(vendor_name_error):
            for k, v in vendor_s_email_error.items():
                result_vendor_name_error.append(['Error in row {}: '
                                                    'Name {} already exist. '
                                                    'Please correct the error and try again'.format(v, k)])
        # Main parsing start
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
                if key == "Country":
                    if value not in COUNTRIES_LIST:
                        country_error.append(['Error in row {}: '
                                              'Country name {} not valid. '
                                              'Please correct the error and try again'.format(count, value)])

            result_dict.append(rows)
        if len(vendor_error) or len(email_error) or len(country_error):
            raise ParseError(detail={'error': [vendor_error, email_error, country_error]})

        if len(result_vendor_name_error) or len(result_vendor_email_error):
            raise ParseError(detail={'error': [result_vendor_name_error, result_vendor_email_error]})

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


def rfi_csv_file_parser(file):
    vendor_error = []
    round_error = []
    status_error = []
    status = ['true', 'false']
    csv_fields = [
                  'Round',
                  'Vendor',
                  'Sourcing',
                  'SA',
                  'SXM',
                  'CLM',
                  'ePRO',
                  'I2P',
                  'P2P',
                  'SPT',
                  'S2P',
                  'AP',
                  'TS',
                  'SOW',
                  'ICW',
                 ]
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        # check the csv file header is equal for template
        if headers != csv_fields:
            raise ParseError('Wrong fields in csv file.')
        # check the csv file modules list
        csv_header_modules=reader.fieldnames[2:]
        csv_header_modules.sort()
        modules_list.sort()

        if csv_header_modules != modules_list:
            raise ParseError('Unknown Module name:  the system could not find the '
                             'Module with such a name in the database.')
        response = []
        for count, rows in enumerate(reader, 1):
            line_info = []
            line_modules = []
            for key, value in rows.items():
                if key == 'Round':
                    if Rfis.objects.filter(rfiid=value):
                        rfi = value
                    else:
                        round_error.append('Unknown Vendor name: the system could not find the Vendor with such a name'
                                           'in the database.  Check the {} line field {}'.format(count, value))
                if key == 'Vendor':
                    if Vendors.objects.filter(vendor_name=value):
                        vendor = value
                    else:
                        vendor_error.append('Unknown Vendor name: the system could not find the Vendor with such a '
                                            'name in the database.  Check the {} line field {}'.format(count, value))
                if key in csv_header_modules:
                    if value not in status:
                        status_error.append('Unknown module status. Check the {} line field {}'.format(count, value))
                    line_modules.append([key, value])
            for m in line_modules:
                d = {"rfi": rfi, "vendor": vendor, "m": m[0], "active": m[1]}
                line_info.append(d)
            response.append(line_info)
        if len(vendor_error) or len(round_error) or len(status_error):
            raise ParseError(detail={'The file could not be uploaded': [vendor_error, round_error, status_error]})
        return response