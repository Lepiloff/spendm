import json
from datetime import date
import datetime

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.db import IntegrityError

from rest_framework.test import APITestCase
from rest_framework import status

from apps.vendors.models import Vendors, VendorContacts, Modules, Rfis, RfiParticipation
from service.csv_file_download import csv_file_parser
from apps.c_users.models import CustomUser


file = 'sample_vendors_test.csv'


class VendorManualCreateTest(APITestCase):
    """ Test module for Vendors model manual create """

    def setUp(self):
        password = 'mypassword'
        vendor = Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12", active=True)
        VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test1@rgmail.com", vendor=vendor)
        CustomUser.objects.create_superuser('myemail@test.com', password)
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)


    def test_vendors_created_success(self):
        vendors_count = Vendors.objects.all().count()
        self.assertEqual(vendors_count, 1)

    def test_vendor_create_name_unique(self):
        with self.assertRaises(IntegrityError):
            Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12",)

    def test_vendor_contact_email_create_unique(self):
        vendor = Vendors.objects.create(vendor_name="U2R", country="Belarus", nda="2020-12-12")
        data ={
            "vendor": vendor.vendorid,
            "contact_name": "Sandra B",
            "phone": 375293333333,
            "email": "testemail@rgmail.com",
            "primary": False
          }
        VendorContacts.objects.create(contact_name="Any", phone="2373823", email="testemail@rgmail.com", vendor=vendor)
        url = reverse('contact_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vendor.active = True
        vendor.save()
        response = self.client.post(url, data, format='json')
        self.assertEqual(json.loads(response.content),
                         {'email': ['Email testemail@rgmail.com already exists']})

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
        self.assertEqual((field1['modules'][0]['module']), 'Strategic Sourcing')
        self.assertEqual((field2['modules'][0]['module']), '')
        self.assertTrue((type(field2['nda']), 'str'))


class VendorCsvCreateTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        CustomUser.objects.create_superuser('myemail@test.com', password)
        Modules.objects.get_or_create(module_name='Strategic Sourcing')
        Modules.objects.get_or_create(module_name='Supplier Management')

        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_vendor_from_csv_create_api(self):
        data = [
    {
        "vendor_name": "Tefstfdstest43",
        "country": "Belarus",
        "nda": "2019-12-24",
        "modules": [
            {
                "module": "Strategic Sourcing"
            },
            {
                "module": "Supplier Management"
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
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

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
        vendor = Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12", active=True)
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
        self.assertEqual(json.loads(response.content),
                         {'email': ['Email testtests@rgmail.com already exists']})
        self.assertEqual(VendorContacts.objects.count(), 1)


class VendorProfileUpdateViewTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_check_partial_update_api(self):
        data = {"vendor_name": "UN"}
        vendor = Vendors.objects.create(vendor_name="U4", country="Belarus", nda="2020-12-12", )
        VendorContacts.objects.create(contact_name="Mrk", phone="2373823", email="test@gmail.com", vendor=vendor)
        _id = vendor.vendorid
        url = reverse('vendor_update',  kwargs={'vendorid': _id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        vendor = Vendors.objects.get(vendorid=_id)
        self.assertEqual(vendor.vendor_name, 'UN')


class ContactsUpdateViewTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_contact_partial_update_api(self):
        data = {"email": "jac12k1@gmail.com"}
        vendor = Vendors.objects.create(vendor_name="U5", country="Belarus", nda="2020-12-12", active=True)
        contact = VendorContacts.objects.create(contact_name="Mrk", phone="-2373823", email="testtest@gmail.com",
                                                vendor=vendor)
        _id = contact.contact_id
        url = reverse('contact_update', kwargs={'contact_id': _id})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        contact = VendorContacts.objects.get(contact_id=_id)
        self.assertEqual(contact.email, 'jac12k1@gmail.com')


class VendorProfileModulesListCreateTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_associate_module_to_round(self):
        password = 'mypassword'
        CustomUser.objects.create_superuser('myemail@test.com', password)
        round = Rfis.objects.create(rfiid="20R1")
        m, _ = Modules.objects.get_or_create(module_name='Sourcing')
        vendor = Vendors.objects.create(vendor_name="U2", country="Belarus", nda="2020-12-12", active=True)
        _id =vendor.vendorid
        data = {
            "active": False,
            "rfi": round.rfiid,
            "vendor": _id,
            "m": m.mid
        }
        url = reverse('modules_to_vendor', kwargs={"vendorid": _id})
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class NewRfiRoundCreateViewTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_create_new_rfi(self):
        data = {
            "issue_datetime": "2020-04-25T10:52:49.677955Z",
            "open_datetime": "2020-03-10T16:06:01+03:00",
            "close_datetime": "2020-03-10T16:06:01+03:00"
        }

        self.assertEqual(Rfis.objects.count(), 0)
        url = reverse('rfi_create')
        response = self.client.post(url, data, format='json')
        self.assertEqual(Rfis.objects.count(), 1)

    def test_create_round_number_api(self):
        data = {
                "issue_datetime": "2020-04-25T10:52:49.677955Z",
                "open_datetime": "2020-03-10T16:06:01+03:00",
                "close_datetime": "2020-03-10T16:06:01+03:00"
               }
        url = reverse('rfi_create')
        self.client.post(url, data, format='json')
        round = Rfis.objects.all().first()
        self.assertEqual(round.rfiid, "20R1")
        self.client.post(url, data, format='json')
        round = Rfis.objects.all().order_by('-timestamp').first()
        self.assertEqual(round.rfiid, "20R2")


class RfiRoundCloseTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_rfi_round_close_api(self):
        data = {
            "issue_datetime": "2020-04-25T10:52:49.677955Z",
            "open_datetime": "2020-03-10T16:06:01+03:00",
            "close_datetime": "2020-03-10T16:06:01+03:00"
        }
        url = reverse('rfi_create')
        self.client.post(url, data, format='json')
        self.assertEqual(Rfis.objects.all().count(), 1)
        round = Rfis.objects.all().first()
        rfiid = round.rfiid
        data = {"active": False}
        url = reverse('rfi_close', kwargs={"rfiid": rfiid})
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        round = Rfis.objects.get(rfiid=rfiid)
        self.assertEqual(round.active, False)

    def test_rount_status_close_not_show(self):
        data = {
                "issue_datetime": "2020-04-25T10:52:49.677955Z",
                "open_datetime": "2020-03-10T16:06:01+03:00",
                "close_datetime": "2020-03-10T16:06:01+03:00",
                "active": False
               }
        url = reverse('rfi_create')
        self.client.post(url, data, format='json')
        self.assertEqual(Rfis.objects.all().count(), 1)
        response = self.client.get(url)
        self.assertEqual(response.content, b'[]')


class VendorManagementScreenTest(APITestCase):
    def setUp(self):
        password = 'mypassword'
        self.user = CustomUser.objects.create_user('myemaidfdsl@test.com', password)
        self.client.force_authenticate(self.user)

    def test_url_get_success_response(self):
        url = reverse('vendor_management_screen')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.content, b'[]')

    def test_get_actual_information_api(self):
        vendor = Vendors.objects.create(vendor_name="U4", country="Belarus", nda="2020-12-12", )
        m1, _ = Modules.objects.get_or_create(module_name='Strategic Sourcing')
        m2, _ = Modules.objects.get_or_create(module_name='Supplier Management')
        round = Rfis.objects.create(rfiid="20R1")
        rfi = RfiParticipation.objects.create(vendor=vendor, rfi=round, m=m1)
        self.assertEqual(RfiParticipation.objects.all().count(), 1)
        url = reverse('vendor_management_screen')
        response = self.client.get(url)
        self.assertEqual(json.loads(response.content)[0]['vendor_name'], 'U4')
