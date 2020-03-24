import json

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError

from rest_framework.test import APITestCase
from rest_framework import status

from apps.vendors.models import Vendors, VendorContacts, Modules
from service.csv_file_download import csv_file_parser
from apps.c_users.models import CustomUser


file = 'sample_vendors_test.csv'


class VendorManualCreateTest(APITestCase):
    """ Test module for Vendors model manual create """

    def setUp(self):
        password = 'mypassword'
        vendor = Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12", )
        VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test1@rgmail.com", vendor=vendor)
        CustomUser.objects.create_superuser('myemail@test.com', password)

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
            "contacts": [{"contact_name": "Mrk", "phone": "2373823", "email": "dRqT@rgmail.com"}
                         ]
        }
        url = reverse('vendor_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendors.objects.count(), 2)


class VendorCsvValidateTest(TestCase):

    def test_csv_parser(self):
        response = csv_file_parser(file)
        field1 = response[0]
        field2 = response[1]
        self.assertEqual((field1['vendor_name']), 'Testtest')
        self.assertEqual((field2['vendor_name']), 'Test2test')
        self.assertEqual((field1['modules'][0]['module']), 'Sourcing')
        self.assertEqual((field2['modules'][0]['module']), '')
        self.assertTrue((type(field2['nda']), 'str'))


class VendorCsvCreateTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        CustomUser.objects.create_superuser('myemail@test.com', password)
        Modules.objects.create(module_name='Sourcing')
        Modules.objects.create(module_name='SA')


    #API
    def test_vendor_from_csv_create(self):
        data = [
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
                "primary": True
            },
            {
                "email": "j45ack213@gmail.com",
                "contact_name": "",
                "primary": False
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
                "primary": True
            },
            {
                "email": "sa1nd54r13a@gmail.com",
                "contact_name": "Sandra Bullock",
                "primary": False
            }
        ]
    }
]

        url = reverse('csv_vendor_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Vendors.objects.count(), 2)


class VendorContactsCreateViewTest(APITestCase):

    # def setUp(self):
        # vendor = Vendors.objects.create(vendor_name="U1", country="Belarus", nda="2020-12-12", )
        # VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test1@rgmail.com", vendor=vendor)

    def test_create_new_contact_api(self):
        vendor = Vendors.objects.create(vendor_name="U1", country="Belarus", nda="2020-12-12", )
        _id = vendor.vendorid
        data = {"vendor": _id,
                "contact_name": "Sandra B",
                "phone": 37529454675,
                "email": "test2@rgmail.com",
                "primary": False
                }
        url = reverse('contact_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(VendorContacts.objects.count(), 1)

    def test_create_new_contact_duplicate_email_check_api(self):
        vendor = Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12", )
        VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="testtests@rgmail.com", vendor=vendor)
        _id = vendor.vendorid
        data = {"vendor": _id,
                "contact_name": "Sandra B",
                "phone": 37529454675,
                "email": "testtests@rgmail.com",
                "primary": False
                }
        url = reverse('contact_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(json.loads(response.content), {'email': ['Email testtests@rgmail.com already exists']})
        self.assertEqual(VendorContacts.objects.count(), 1)


class VendorProfileUpdateViewTest(APITestCase):

    def test_check_partial_update_api(self):
        data = {"nda": "2020-11-11"}
        vendor = Vendors.objects.create(vendor_name="U4", country="Belarus", nda="2020-12-12", )
        VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test@gmail.com", vendor=vendor)
        _id = vendor.vendorid
        url = reverse('vendor_update',  kwargs={'vendorid': _id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(vendor.nda, '2020-11-11')


class ContactsUpdateViewTest(APITestCase):

    def test_contact_partial_update_api(self):
        data = {"email": "jac12k1@gmail.com"}
        vendor = Vendors.objects.create(vendor_name="U5", country="Belarus", nda="2020-12-12", )
        contact = VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="testtest@gmail.com",
                                                vendor=vendor)
        _id = contact.contact_id
        url = reverse('contact_update', kwargs={'contact_id': _id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(contact.email, 'jac12k1@gmail.com')
