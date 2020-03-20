import json

from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.exceptions import ParseError
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework import status

from apps.c_users.models import CustomUser
from service.csv_file_download import csv_file_parser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules
from .serializers import VendorsSerializer, VendorToFrontSerializer, VendorsCsvSerializer, ModulesSerializer


class AdministratorDashboard(APIView):

    def get(self, request, format=None):
        vendors = [vendor.vendor_name for vendor in Vendors.objects.all()]
        return Response(vendors)


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # renderer_classes = [JSONRenderer]
    permission_classes = (permissions.AllowAny,)
    serializer_class = VendorsCsvSerializer

    def put(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")
        f = request.data['file']
        filename = f.name
        if filename.endswith('.csv'):
            file = default_storage.save(filename, f)
            r = csv_file_parser(file)
            status = 204
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
    serializer_class = VendorsSerializer

    def post(self, request, *args, **kwargs):
        data = request.data
        if data['nda'] == '':
            data['nda'] = None
        for contact in data['contacts']:
            if contact['email']:
                contact['email'] = contact['email'].lower()
        serializer = VendorsSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)


class VendorsToFrontView(generics.ListAPIView):
    """ Get Vendors list for frontend validation"""
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


