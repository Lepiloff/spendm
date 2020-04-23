import csv
import pandas as pd
import re
from datetime import date
import datetime

from rest_framework.exceptions import ParseError

from apps.vendors.models import Vendors, VendorContacts, Rfis
from service.countries import COUNTRIES_LIST

modules_list = [
    "Strategic Sourcing",
    "Supplier Management",
    "Spend Analytics",
    "Contract Management",
    "e-Procurement",
    "Invoice-to-Pay",
    "Strategic Procurement",
    "Technologies",
    "Procure-to-Pay",
    "Source-to-Pay",
]


def csv_file_parser(file):
    vendor_error = []
    email_error = []
    country_error = []
    date_error = []
    missing_value = []
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

        # Check empty file
        df = pd.read_csv(file)  # or pd.read_excel(filename) for xls file
        if df.empty:
            raise ParseError("File is empty")
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
                result_vendor_email_error.append('Error in row {}: '
                                                    'Email {} already exist. '
                                                    'Please correct the error and try again'.format(v, k))
        if len(vendor_p_email_error):
            for k, v in vendor_p_email_error.items():
                result_vendor_email_error.append('Error in row {}: '
                                                    'Email {} already exist. '
                                                    'Please correct the error and try again'.format(v, k))
        if len(vendor_name_error):
            for k, v in vendor_s_email_error.items():
                result_vendor_name_error.append('Error in row {}: '
                                                    'Name {} already exist. '
                                                    'Please correct the error and try again'.format(v, k))
        # Main parsing start
        for count, rows in enumerate(reader, 1):
            for key, value in rows.items():
                if not rows[key]:
                    if key == 'NDA date' or key == 'Secondary Contact Name' or key == 'Secondary Contact Email' \
                            or key == 'Modules':
                        pass
                    else:
                        missing_value.append('Missing value in file! Check the {} line field {}'.format(count, key))
                        # raise ParseError('Missing value in file! Check the {} line field {}'.format(count, key))
                if key == 'Modules':
                    if value != '':
                        for v in value.split(','):
                            if v not in modules_list:
                                raise ParseError(
                                    'Check the Modules field value. Accepted value are: {}'.format(modules_list))

                if key == "Vendor":
                    vendor = Vendors.objects.filter(vendor_name=value).first()
                    if vendor:
                        vendor_error.append('Error in row {}: '
                                             'Vendor {} already exist. '
                                             'Please correct the error and try again'.format(count, value))
                if key == "Primary Contact Email" or key == "Secondary Contact Email":
                    if len(value) > 80:
                        email_error.append('Error in row {}: '
                                            'Email {} is not in the right format. '
                                            'The value cannot be longer than 80 characters.'
                                            'Please correct the error and try again'.format(count, value))
                    if not re.search(r'^$|[^@]+@[^\.]+\..+', value):
                        email_error.append('Error in row {}: '
                                            'Email {} is not in the right format. '
                                            'Please correct the error and try again'.format(count, value))
                    if value != "":
                        email = VendorContacts.objects.filter(email=value).first()
                        if email:
                            email_error.append('Error in row {}: '
                                                'Email {} already exist. '
                                                'Please correct the error and try again'.format(count, value))
                if key == "Country":
                    if value not in COUNTRIES_LIST:
                        country_error.append('Error in row {}: '
                                              'Country name {} not valid. '
                                              'Please correct the error and try again'.format(count, value))
                if key == "NDA date":
                    if re.search(r'^$|\d{4}-\d{2}-\d{2}', value):  # regular expression for date
                        if value != '':
                            curent_date = datetime.date.today()
                            csv_date = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                            if csv_date > curent_date:
                                 date_error.append('Error in row {}: '
                                                    'date {} can no be more then future NDA date. '
                                                    'Please correct the error and try again'.format(count, value))
                    else:
                        date_error.append('Error in row {}: '
                                           'date {} not valid. '
                                           'Please correct the error and try again'.format(count, value))

            result_dict.append(rows)
        if len(vendor_error) or len(email_error) or len(country_error) or len(date_error):
            error_pre_formatted_list = [vendor_error, email_error, country_error, date_error]
            error_formatted_list = [", ".join(x) for x in error_pre_formatted_list]
            raise ParseError(detail={'general_errors': error_formatted_list})

        if len(result_vendor_name_error) or len(result_vendor_email_error):
            pandas_error_pre_formatted_list = [result_vendor_name_error, result_vendor_email_error]
            error_formatted_list = [", ".join(x) for x in pandas_error_pre_formatted_list]
            raise ParseError(detail={'general_errors': error_formatted_list})

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
                    "Round",
                    "Vendor",
                    "Strategic Sourcing",
                    "Supplier Management",
                    "Spend Analytics",
                    "Contract Management",
                    "e-Procurement",
                    "Invoice-to-Pay",
                    "Strategic Procurement",
                    "Technologies",
                    "Procure-to-Pay",
                    "Source-to-Pay",
                 ]
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        headers = reader.fieldnames
        # check the csv file header is equal for template
        if headers != csv_fields:
            raise ParseError('Wrong fields in csv file.')
        # check the csv file modules list
        csv_header_modules = reader.fieldnames[2:]
        csv_header_modules.sort()
        modules_list.sort()

        if csv_header_modules != modules_list:
            raise ParseError('Unknown Module name:  the system could not find the '
                             'Module with such a name in the database.')

        # Check all row round values? before strting processing because if round is incorrect
        # rfi variables in code return 500 error (local variable 'rfi' referenced before assignment)
        for count, rows in enumerate(reader, 1):
            for key, value in rows.items():
                if key == 'Round':
                    round = Rfis.objects.filter(rfiid=value)
                    if not round:
                        round_error.append('Inapplicable Round: the system should accept uploaded changes only for the '
                                           'current round. Check the {} line field {}'.format(count, value))
        if len(round_error):
            raise ParseError(
                detail={'general_errors': round_error})
        # Next two string allow using opened csv file twice
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        response = []
        for count, rows in enumerate(reader, 1):
            line_info = []
            line_modules = []
            for key, value in rows.items():
                if key == 'Round':
                    if Rfis.objects.filter(rfiid=value):
                        rfi = value
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
        if len(vendor_error) and len(status_error):
            raise ParseError(detail={'general_errors': [vendor_error, status_error]})
        elif len(vendor_error):
            raise ParseError(detail={'general_errors': vendor_error})
        elif len(status_error):
            raise ParseError(detail={'general_errors': status_error})
        return response