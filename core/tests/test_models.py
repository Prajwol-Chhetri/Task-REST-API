from django.test import TestCase
from django.contrib.auth import get_user_model

class ModelTests(TestCase):
    
    def test_create_user_with_email_successful(self):
        """Test creating a new user with email is successful"""
        email = 'test@mytestapp.com'
        password = 'Testpass123'
        first_name = 'Test'
        last_name = 'API'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Tests the email for new user is normalized"""
        email = 'test@MYTESTAPP.COM'
        first_name = 'Test'
        last_name = 'API'
        user = get_user_model().objects.create_user(email, 'test123', first_name, last_name)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123', 'Test', 'API')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@testing.com',
            'test123',
            'Test',
            'User'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
