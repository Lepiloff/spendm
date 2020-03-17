from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError

from rest_framework.test import APITestCase
from rest_framework import status

from apps.vendors.models import Vendors, VendorContacts
from apps.c_users.models import CustomUser
from apps.vendors.serializers import VendorsSerializer


client = Client()


class VendorManualTestCase(APITestCase):
    """ Test module for Vendors model manual create """

    def setUp(self):
        vendor = Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12", )
        VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test1@rgmail.com", vendor=vendor)

    def test_vendors_created_success(self):
        vendors_count = Vendors.objects.all().count()
        self.assertEqual(vendors_count, 1)

    def test_vendor_create_name_unique(self):
        with self.assertRaises(IntegrityError):
            Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12",)

    def test_vendor_contact_email_create_unique(self):
        vendor = Vendors.objects.create(vendor_name="U2R", country="Belarus", nda="2020-12-12", )
        with self.assertRaises(IntegrityError):
            VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test1@rgmail.com",
                                          vendor=vendor)
    #API
    def test_create_vendor_api(self):

        data = {
            "vendor_name": "TestName",
            "country": "Belarus",
            "nda": "2020-12-12",
            "parent": "",
            "contacts": [{"contact_name": "Mrk", "phone": "2373823", "email": "dRqT@rgmail.com"},
                         {"contact_name": "Uio", "phone": "34567", "email": "rdq@gmail.com"}
                         ]
        }
        url = reverse('vendor_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendors.objects.count(), 2)




    # def setUp(self):
    #     data = {
    #         "vendor_name": "U2",
    #         "country": "Belarus",
    #         "nda": "2020-12-12",
    #         "parent": "",
    #         "contacts": [{"contact_name": "Mrk", "phone": "2373823", "email": "dRqT@rgmail.com"},
    #                      {
    #                          "contact_name": "Uio",
    #                          "phone": "3q4567",
    #                          "email": "rdq@gmail.com"
    #                      }
    #                      ]
    #     }
    #     # contact = data['contacts']
    #     # for c in contact:
    #     #     VendorContacts.objects.create(data=c)
    #     vendor_data = data.pop('contacts')
    #     Vendors.objects.create(data=vendor_data)
    #     # Vendors.objects.create(data=data, parent=1)
    #
    # def test_vendors_created_count(self):
    #     vendors_count = Vendors.objects.all().count()
    #     self.assertEqual(vendors_count, 1)
    #
    # def test_get_all_vendors(self):
    #     # get API response
    #     response = client.get(reverse('vendors_list'))
    #     # get data from db
    #     vendors = Vendors.objects.all()
    #     serializer = VendorsSerializer(vendors, many=True)
    #     self.assertEqual(response.data, serializer.data)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
