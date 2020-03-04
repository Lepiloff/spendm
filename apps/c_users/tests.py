import mock
from functools import partial
import datetime

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework_simplejwt.tokens import aware_utcnow

from apps.c_users.models import CustomUser


class TestLoginCase(APITestCase):

    login_url = reverse('token_obtain_pair')
    refresh_token_url = reverse('token_refresh')
    logout_url = reverse('user_logout')
    profile_url = reverse('custom_users')

    email = 'test@user.com'
    password = 'kah2ie3urh4k'

    def setUp(self):
        self.user = CustomUser.objects.create_user(self.email, self.password)

    def _login(self):
        data = {
            'email': self.email, 'password': self.password
        }
        r = self.client.post(self.login_url, data)
        body = r.json()
        if 'access' in body:
            self.client.credentials(
                HTTP_AUTHORIZATION='Bearer %s' % body['access'])
        return r.status_code, body

    def test_login1(self):
        response = self.client.post(self.login_url, {'email': self.email, 'password': self.password}, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_wrong_login_email(self):
        response = self.client.post(self.login_url, {'email': 'wrong@email.com', 'password': self.password}, follow=True)
        self.assertEqual(response.status_code, 401)

    def test_wrong_login_pass(self):
        response = self.client.post(self.login_url, {'email': self.email, 'password': 'wrongpass'}, follow=True)
        self.assertEqual(response.status_code, 401)

    def test_logout_response_200(self):
        _, body = self._login()
        data = {'refresh': body['refresh']}
        r = self.client.post(self.logout_url, data)
        body = r.content
        self.assertEquals(r.status_code, 204, body)
        self.assertFalse(body, body)

    def test_logout_with_bad_refresh_token_response_400(self):
        self._login()
        data = {'refresh': 'dsf.sdfsdf.sdf'}
        r = self.client.post(self.logout_url, data)
        body = r.json()
        self.assertEquals(r.status_code, 400, body)
        self.assertTrue(body, body)

    def test_logout_refresh_token_in_blacklist(self):
        _, body = self._login()
        r = self.client.post(self.logout_url, body)
        token = partial(RefreshToken, body['refresh'])
        self.assertRaises(TokenError, token)

    def test_access_token_still_valid_after_logout(self):
        _, body = self._login()
        self.client.post(self.logout_url, body)
        r = self.client.get(self.profile_url)
        body = r.json()
        self.assertEquals(r.status_code, 200, body)
        self.assertTrue(body, body)

    def test_access_token_invalid_in_hour_after_logout(self):
        _, body = self._login()
        self.client.post(self.logout_url, body)
        m = mock.Mock()
        m.return_value = aware_utcnow() + datetime.timedelta(minutes=60)
        with mock.patch('rest_framework_simplejwt.tokens.aware_utcnow', m):
            r = self.client.get(self.profile_url)
            body = r.json()
        self.assertEquals(r.status_code, 401, body)
        self.assertTrue(body, body)
