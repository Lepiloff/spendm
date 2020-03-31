from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.exceptions import ParseError
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status

from service.csv_file_download import csv_file_parser
from .models import Vendors, VendorContacts, Modules, VendorModuleNames, Rfis, RfiParticipation
from .serializers import VendorsCreateSerializer, VendorToFrontSerializer, VendorsCsvSerializer, ModulesSerializer, \
    VendorsManagementListSerializer, VendorManagementUpdateSerializer, VendorContactSerializer, \
    VendorContactCreateSerializer, RfiRoundSerializer, RfiRoundCloseSerializer, VendorModulesListManagementSerializer, \
    RfiParticipationSerializer


class AdministratorDashboard(APIView):

    def get(self, request, format=None):
        vendors = [vendor.vendor_name for vendor in Vendors.objects.all()]
        return Response(vendors)


class FileUploadView(APIView):
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
                r = csv_file_parser(file)
                status = 200
            finally:
                default_storage.delete(file)
        else:
            status = 406
            r = "File format error"
        return Response(r, status=status)


# Using serializer
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
            try:
                serializer.is_valid(raise_exception=True)
                serializer.save()
            except ValidationError:
                return Response({"errors": (serializer.errors,)},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)


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
        if data['nda'] == '':
            data['nda'] = None
        for contact in data['contacts']:
            if contact['email']:
                contact['email'] = contact['email'].lower()
        serializer = VendorsCreateSerializer(data=data)
        try:
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

    data = {
        "active": false,
        "rfi": "20R1",
        "vendor": 15,
        "m": 4
        }
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = RfiParticipationSerializer

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


# RFI MANAGEMENT

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

