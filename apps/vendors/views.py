import csv
import json

from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction


from rest_framework import permissions
from rest_framework.exceptions import ParseError
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status

from service.csv_file_download import csv_file_parser, rfi_csv_file_parser
from service.xml_file_upload_downlod import parse_excel_rfi_sheet, InvalidFormatException
from .models import Vendors, VendorContacts, Modules, VendorModuleNames, Rfis, RfiParticipation
from .serializers import VendorsCreateSerializer, VendorToFrontSerializer, VendorsCsvSerializer, ModulesSerializer, \
    VendorsManagementListSerializer, VendorManagementUpdateSerializer, VendorContactSerializer, \
    VendorContactCreateSerializer, RfiRoundSerializer, RfiRoundCloseSerializer, VendorModulesListManagementSerializer, \
    RfiParticipationSerializer, RfiParticipationCsvSerializer, RfiParticipationCsvDownloadSerializer


class AdministratorDashboard(APIView):

    def get(self, request, format=None):
        vendors = [vendor.vendor_name for vendor in Vendors.objects.all()]
        return Response(vendors)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.AllowAny,)

    def put(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        f = request.data['file']
        filename = f.name
        if filename.endswith('.csv'):
            try:
                file = default_storage.save(filename, f)
                r = csv_file_parser(file)
                status = 200
            finally:
                default_storage.delete(file)
        else:
            status = 406
            r = {"general_errors": ["Please upload only CSV files"]}
        return Response(r, status=status)


class ExcelFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.AllowAny,)

    def put(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        f = request.data['file']
        filename = f.name
        if filename.endswith('.xlsx'):
            try:
                file = default_storage.save(filename, f)
                r = parse_excel_rfi_sheet(file)
                status = 200
            except InvalidFormatException as e:
                r = {"general_errors": [e.__str__()]}
                status = 406
            except Exception as e:
                r = {"general_errors": [e.__str__()]}
                status = 406
            finally:
                default_storage.delete(file)
        else:
            status = 406
            r = {"general_errors": ["Please upload only xlsx files"]}
        return Response(r, status=status)


class CsvToDatabase(APIView):
    """
[
    {
        "vendor_name": "Tefstfdstest43",
        "country": "Belarus",
        "nda": "2019-12-24",
        "modules": [
            {
                "module": "Sourcing"
            },
            {
                "module": "SA"
            }
        ],
        "contacts": [
            {
                "email": "jack15621@gmail.com",
                "contact_name": "Jack Jhonson",
                "primary": true
            },
            {
                "email": "j45ack213@gmail.com",
                "contact_name": "",
                "primary": false
            }
        ]
    },
    {
        "vendor_name": "Tesddt7t2test",
        "country": "Canada",
        "nda": "",
        "modules": [
            {
                "module": ""
            }
        ],
        "contacts": [
            {
                "email": "sand45r2a1@gmail.com",
                "contact_name": "Sandra Bullock",
                "primary": true
            },
            {
                "email": "sa1nd54r13a@gmail.com",
                "contact_name": "Sandra Bullock",
                "primary": false
            }
        ]
    }
]
    """

    permission_classes = (permissions.AllowAny,)
    serializer_class = VendorsCsvSerializer

    def post(self, request, format=None):
        r_data = request.data
        try:
            # implement transaction  - if exception appear during for loop iteration none data save to DB
            with transaction.atomic():
                for data in r_data:
                    if data['nda'] == '':
                        data['nda'] = None
                    for contact in data['contacts']:
                        if contact['email']:
                            contact['email'] = contact['email'].lower()
                    for module in data['modules']:
                        if module['module']:
                            module['module'] = get_object_or_404(Modules, module_name=module['module']).mid
                        else:
                            data.pop('modules')
                    serializer = VendorsCsvSerializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)


class VendorsCreateView(APIView):
    """
    parameters {
            "vendor_name": "Uf2r63",
            "country": "Belarus",
            "nda": "2020-12-12",
            "parent": "",
            "contacts": [{"contact_name": "Mrk", "phone": "2373823", "email": "dtrfd@rgmail.com"},
                         {"contact_name": "Uio", "phone": "3q4567", "email": "ddttcyf@gmail.com" }
                         ]
                }

    responses = {
                "vendor_name": "Uf2r63",
                "country": "Belarus",
                "nda": "2020-12-12",
                "parent": "",
                "contacts": [
                    {
                        "contact_name": "Mrk",
                        "phone": "2373823",
                        "email": "dtrfd@rgmail.com"
                    },
                    {
                        "contact_name": "Uio",
                        "phone": "3q4567",
                        "email": "ddttcyf@gmail.com"
                        }
                    ]
                }
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = VendorsCreateSerializer

    def post(self, request, *args, **kwargs):
        data = request.data

        try:
            # implement transaction  - if exception appearpyt during for loop iteration none data save to DB
            with transaction.atomic():
                if data['nda'] == '':
                    data['nda'] = None
                for contact in data['contacts']:
                    if contact['email']:
                        contact['email'] = contact['email'].lower()
                serializer = VendorsCreateSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)


class VendorsToFrontView(generics.ListAPIView):
    """
    Get Vendors list for frontend validation
    """
    queryset = Vendors.objects.all()
    serializer_class = VendorToFrontSerializer
    permission_classes = [permissions.AllowAny, ]


class ModulesListView(generics.ListAPIView):
    """
    Get list of all exist modules
    """
    queryset = Modules.objects.all()
    serializer_class = ModulesSerializer
    permission_classes = [permissions.AllowAny, ]


# <--VENDOR PROFILE-->
class VendorProfilePageView(generics.RetrieveAPIView):
    """ Get vendor Profile personal data"""

    serializer_class = VendorContactSerializer
    permission_classes = [permissions.AllowAny, ]
    lookup_field = "vendorid"

    def get_object(self):
        obj = get_object_or_404(VendorContacts, vendor=self.kwargs["vendorid"], primary=True)
        return obj


class VendorManagementListScreen(generics.ListAPIView):
    """n
    Get Vendors Management screen
    """
    serializer_class = VendorsManagementListSerializer
    queryset = Vendors.objects.all()
    permission_classes = [permissions.AllowAny, ]


class VendorProfileUpdateView(generics.RetrieveUpdateAPIView):
    """ Update main vendor info (exclude contact)

    GET:
       {
        "vendorid": 118,
        "vendor_name": "rdty",
        "active": true,
        "country": "Belarus",
        "office": "",
        "abr_date": null,
        "nda": "2020-12-12",
        "parent": null,
        "contacts": [],
        "to_vendor": [
            {
                "pk": 3,
                "active": true,
                "m": "Sourcing",
                "rfi": "20R1",
                "vendor": 118,
                "timestamp": "2020-04-06T12:50:14.762535"
            },
            {
                "pk": 4,
                "active": true,
                "m": "SA",
                "rfi": "20R1",
                "vendor": 118,
                "timestamp": "2020-04-06T13:57:33.988896"
            }
        ],
        "history": [
                {
                    "vendor_name": "rty"
                },
                {
                    "vendor_name": "TTT"
                }
            ],
    "current_round_participate": false
    }



    PUT (PATH):
    Possible send partial data (just one field)
    data = {
            "vendor_name":"Forest G"
           }
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = VendorManagementUpdateSerializer
    lookup_field = 'vendorid'

    def get_queryset(self):
        vendorid = self.kwargs['vendorid']
        return Vendors.objects.filter(vendorid=vendorid)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class VendorContactsCreateView(APIView):
    """
    Create new vendor from Vendor Manager screen

      {
        "vendor": 138,
        "contact_name": "Sandra B",
        "phone": 375293333333,
        "email": "sand3f45r2a1@gmail.com",
        "primary": false
      }

    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = VendorContactCreateSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        serializer = VendorContactCreateSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(request.data, status=status.HTTP_200_OK)


class ContactsUpdateView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get or update exist contact at Vendor Management Screen
    Possible send partial data (just one field) (PUT or PATH method)
    data = {
        "contact_name": "Name"
        }

    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = VendorContactSerializer
    lookup_field = 'contact_id'
    queryset = VendorContacts.objects.all()

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class VendorProfileModulesListCreate(generics.ListCreateAPIView):
    """View Vendor profile modules activity status and update it
    POST:
        data = {
            "active": false,
            "rfi": "20R1", # allow send blank field (Null)
            "vendor": 15,
            "m": 4
            }
        """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = RfiParticipationSerializer

    # Implement just to rewrite status code from 201(default) to 200
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)

    def get_queryset(self, **kwargs):
        round = Rfis.objects.all().order_by('-timestamp').first()
        vendor = get_object_or_404(Vendors, vendorid=self.kwargs['vendorid'])
        queryset = RfiParticipation.objects.filter(vendor=vendor, rfi=round)
        return queryset


# <--RFI-->

class NewRfiRoundCreateView(generics.ListCreateAPIView):

    """New RFI round crete

        data = {
                "issue_datetime": "2020-03-25T10:52:49.677955Z",
                "open_datetime": "2020-03-10T16:06:01+03:00",
                "close_datetime": "2020-03-10T16:06:01+03:00"
               }

    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = RfiRoundSerializer
    queryset = Rfis.objects.filter(active=True)


class RfiRoundClose(generics.RetrieveUpdateAPIView):
    """Close rfi round
    data = {"active": False}

    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = RfiRoundCloseSerializer
    queryset = Rfis.objects.all()
    lookup_field = 'rfiid'

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RfiRoundView(generics.RetrieveAPIView):
    """ Rfi round info
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = RfiRoundSerializer
    queryset = Rfis.objects.all()
    lookup_field = 'rfiid'


class RfiRoundListView(generics.ListAPIView):
    """ Rfi round info
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = RfiRoundSerializer
    queryset = Rfis.objects.all()


class AssociateModulesWithVendorView(generics.ListCreateAPIView):
    """
    RFI: List of vendors with participated modules and modules status change method

    POST request data:
    data =  {
                "active": true,
                "m": 1,
                "rfi": "20R1",
                "vendor": 15
             }

    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = VendorModulesListManagementSerializer
    queryset = Vendors.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RfiParticipationSerializer
        return VendorModulesListManagementSerializer


# Rfi Csv
class RfiCsvUploadView(APIView):
    """ Upload rfi csv file"""
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.AllowAny,)
    serializer_class = VendorsCsvSerializer

    def put(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        f = request.data['file']
        filename = f.name
        if filename.endswith('.csv'):
            try:
                file = default_storage.save(filename, f)
                r = rfi_csv_file_parser(file)
                status = 200
            finally:
                default_storage.delete(file)
        else:
            status = 406
            r = { "general_errors": ["Please upload only CSV files"] }
        return Response(r, status=status)


class AssociateModulesWithVendorCsv(APIView):

    """
    Create or update modules to rfi

    data = [
        {
            "rfi": "20R1",
            "module": [
                {
                    "Sourcing": "false"
                },
                {
                    "SA": "true"
                },
                {
                    "SXM": "false"
                }

            ],
            "vendor": "Arny3"
        },
        {
            "rfi": "20R1",
            "module": [
                {
                    "S2P": "false"
                },
                {
                    "AP": "false"
                },
                {
                    "TS": "false"
                },
                {
                    "SOW": "false"
                },
                {
                    "ICW": "true"
                }
            ],
            "vendor": "Mark Shagal"
        }
    ]
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = RfiParticipationCsvSerializer

    def post(self, request, format=None):
        r_data = request.data
        for data in r_data:
            for data in data:
                v = data.get('vendor', None)
                vendor = get_object_or_404(Vendors, vendor_name=v)
                data['vendor'] = vendor.vendorid
                m = data.get('m', None)
                module = get_object_or_404(Modules, module_name=m)
                data['m'] = module.mid
                serializer = RfiParticipationCsvSerializer(data=data)
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                except ValidationError:
                    return Response({"errors": (serializer.errors,)},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)


class CsvRfiTemplateDownload(APIView):


    # TODO filter vendor by round partisipation
    """ Download rfi modules .csv file """

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None, **kwargs):
        rfi = kwargs['rfiid']
        csv_header_fields = ['Round', 'Vendor', 'Sourcing', 'SA', 'SXM', 'CLM', 'ePRO', 'I2P',
                             'P2P', 'SPT', 'S2P', 'AP', 'TS', 'SOW', 'ICW']
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export_rfi.csv"'
        writer = csv.DictWriter(response, fieldnames=csv_header_fields)
        writer.writeheader()
        vendor = Vendors.objects.all()
        for v in vendor:
            vendor_name = v.vendor_name
            module = RfiParticipation.objects.filter(rfi=rfi, vendor=v)
            module_to_vendor = []
            for m in module:
                serializer = RfiParticipationCsvDownloadSerializer(m)
                module_dict = serializer.data.copy()  # get dict object
                module_to_vendor.append(module_dict)
            res = {i['m']: i['active'] for i in module_to_vendor if i.keys() == {'active', 'm'}}
            writer.writerow({'Round': rfi, 'Vendor': vendor_name, 'Sourcing': res.get('Sourcing', False),
                             'SA': res.get('SA', False), 'SXM': res.get('SXM', False),
                             'CLM': res.get('CLM', False), 'ePRO': res.get('ePRO', False),
                             'I2P': res.get('I2P', False), 'P2P': res.get('P2P', False),
                             'SPT': res.get('SPT', False), 'S2P': res.get('S2P', False),
                             'AP': res.get('AP', False), 'TS': res.get('TS', False),
                             'SOW': res.get('SOW', False), 'ICW': res.get('ICW', False)})
        return response


# EXCELL

class CreateElementFromExcellFile(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)