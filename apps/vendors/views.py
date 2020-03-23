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
from .serializers import VendorsCreateSerializer, VendorToFrontSerializer, VendorsCsvSerializer, ModulesSerializer, \
    VendorManagementListSerializer, VendorManagementUpdateSerializer, VendorContactSerializer, VendorContactCreateSerializer


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
            status = 200
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


class VendorManagementList(generics.ListAPIView):
    """
    Get Vendors Management page
    """
    serializer_class = VendorManagementListSerializer
    queryset = Vendors.objects.all()


class VendorProfileUpdateView(generics.RetrieveUpdateAPIView):
    """ Update main vendor info (exclude contact)
    Possible send partial data (just one field)
    {
    "parent": 109
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


class VendorContactsCreateView(generics.CreateAPIView):
    """
    Create new vendor from Vendor Manager screen

      {
            "contact_name": "Sandra B",
            "phone": null,
            "email": "sand3f45r2a1@gmail.com",
            "primary": true

      }

    """
    permission_classes = [permissions.AllowAny, ]
    serializer_class = VendorContactCreateSerializer
    lookup_field = 'vendorid'

    def get_object(self):
        obj = self.kwargs['vendorid']
        return (obj)

    def post(self, request, *args, **kwargs):
        data = request.data
        v_id = self.get_object()
        data.update({'vendor': v_id})
        serializer = VendorContactCreateSerializer(data=data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(request.data, status=status.HTTP_200_OK)


class VendorContactsCreateView(generics.RetrieveUpdateDestroyAPIView):
    """
           { "contact_id": 203,
            "contact_name": "Jack J",
            "phone": null,
            "email": "jac12k1@gmail.com",
            "primary": true }
    """

    permission_classes = [permissions.AllowAny, ]
    serializer_class = VendorContactCreateSerializer
    lookup_field = 'contact_id'
    queryset = VendorContacts.objects.all()


    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)