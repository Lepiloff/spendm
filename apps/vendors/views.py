from collections import deque

from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError

from rest_framework import permissions
from rest_framework.exceptions import ParseError
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer, BrowsableAPIRenderer
from rest_framework import status

from apps.c_users.models import CustomUser
from service.csv_file_download import csv_file_parser, add_vendors_to_database_from_csv
from .models import Vendors, VendorContacts, VendorModuleNames
from .serializers import VendorsSerializer, VendorContactSerializer, VendorModulSerializer, ModulesSerializer


class AdministratorDashboard(APIView):

    def get(self, request, format=None):
        vendors = [vendor.vendor_name for vendor in Vendors.objects.all()]
        return Response(vendors)


class FileUploadView(APIView):
    parser_classes = ( MultiPartParser, FormParser)
    renderer_classes = [JSONRenderer]

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


class _CsvToDatabase(APIView):

    # --> To do make list of dict as a request json
    def post(self, request, format=None):
        data = request.data
        v_list = []
        for _, vendor in data.items():
            v = Vendors(
                vendor_name=vendor['Vendor'],
                country=vendor['Country'],
                nda=vendor['NDA date'],

            )
            # Call the full_clean() method for manual triggered models clean() method
            try:
                v.full_clean()
            except ValidationError as e:
                data = ({'status': str(e)})
                return Response(data, content_type='application/json')
            v.save()
            v_list.append(vendor['Vendor'])
            vc = VendorContacts(
                vendor=v,
                contact_name=vendor['Primary Contact Name'],
                email=vendor['Primary Contact Email'],
                sec_contact_name=vendor['Secondary Contact Name'],
                sec_email=vendor['Secondary Contact Email'],
            ).save()
        return Response({'message':
                        'Vendors from vendors list {} were successfully added to the database'.format(v_list)
                         })


# Using serializer

# --> To do make list of dict as a request json
class CsvToDatabase(APIView):
    renderer_classes = [JSONRenderer]

    def post(self, request, format=None):
        res_serializer = deque()
        for key, data_item in request.data.items():
            serializer = VendorsSerializer(data=data_item)
            if serializer.is_valid():
                res_serializer.append(serializer)
            else:
                raise ParseError('Wrong data received')
        for serializer in res_serializer:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorsCreateView(APIView):
    """Create new vendor instances from form"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = VendorsSerializer

    def post(self, request, *args, **kwargs):
        serializer = VendorsSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError:
            return Response({"errors": (serializer.errors,)},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(request.data, status=status.HTTP_200_OK)
