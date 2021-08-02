from os import access
from django.test import TestCase
from django.contrib.auth import get_user_model, login
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


REGISTER_USER_URL = reverse('auth:register')
LOGIN_URL = reverse('auth:token_obtain_pair')
REFRESH_URL = reverse('auth:token_refresh')
UPDATE_URL = reverse('auth:update')

def register_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self):
        self.client = APIClient()

    def test_register_valid_user_success(self):
        """Test registering user with valid payload is successful"""
        payload = {
            'email': 'test@testing.com',
            'password': 'testpass',
            'first_name': 'Test',
            'last_name': 'Test'
        }
        res = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """Test creating user tht already exists fails"""
        payload = {'email': 'test@testing.com', 'password': 'testpass', 'first_name': 'Test', 'last_name': 'Test'}
        register_user(**payload)

        res = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test that passwords must be more than 5 characters"""
        payload = {
            'email': 'test@testing.com',
            'password': 'pw',
            'first_name': 'Test',
            'last_name': 'Test'
            }
        res = self.client.post(REGISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication"""

    def setUp(self):
        self.user = register_user(
            email='test@testing.com',
            password='testpass',
            first_name='Test',
            last_name='User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    
    def test_login_success(self):
        """Testing log-in is successful and jwt tokens are generated for registered user"""
        payload = {'email': 'test@testing.com', 'password': 'testpass'}
        res = self.client.post(LOGIN_URL, payload)

        self.assertIn('refresh', res.data)
        self.assertIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_login_fail_invalid_credentials(self):
        """Testing log-in fails and jwt tokens are not generated if user provides wrong password"""
        payload = {'email': 'test@testing.com', 'password': '2222222'}
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('refresh', res.data)
        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_fail_missing_field(self):
        """Test that email and password are required"""
        payload = {'email': 'test@testing.com', 'password': ''}
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('refresh', res.data)
        self.assertNotIn('access', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_fail_unauthorized_user(self):
        """Testing log-in fails and jwt tokens are not generated for unauthorized user"""
        payload = {'email': 'unauthorized@testing.com', 'password': 'unauthorizedtestpass'}
        res = self.client.post(LOGIN_URL, payload)

        self.assertNotIn('refresh', res.data)
        self.assertNotIn('access', res.data)   
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        """Test refresh token is generated successfully"""
        payload = {'email': 'test@testing.com', 'password': 'testpass'}
        res = self.client.post(LOGIN_URL, payload)
        refresh_token = {'refresh': res.data['refresh']}
        refresh_res = self.client.post(REFRESH_URL, refresh_token)
        self.assertNotIn('refresh', refresh_res.data)
        self.assertIn('access', refresh_res.data)
        self.assertEqual(refresh_res.status_code, status.HTTP_200_OK)

    def test_update_user_profile(self):
        """Test Updating the user profile for authenticated user"""
        payload = {'email': 'test@testing.com', 'password': 'testpass'}
        res = self.client.post(LOGIN_URL, payload)
        access_token = 'Bearer '+res.data['access']

        updated_payload = {'first_name': 'Changed', 'password': 'newpassword123'}
        header = {'Authorization': access_token}
        update_res = self.client.patch(UPDATE_URL, updated_payload, **header)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, updated_payload['first_name'])
        self.assertTrue(self.user.check_password(updated_payload['password']))
        self.assertEqual(update_res.status_code, status.HTTP_200_OK)