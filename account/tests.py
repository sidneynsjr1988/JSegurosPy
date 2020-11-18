
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('users')
TOKEN_URL = reverse('token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
    Test the users API (public)
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user(self):
        """
        Test creating user with valid payload is successful
        """
        payload = {
            'username': "test",
            'email': 'test@gmail.com',
            'password': 'test12345',
            'name': 'John Doe'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(
            user.check_password(payload['password'])
        )
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        """
        Test creating user that already exists fail
        """
        payload = {
            'username': "test",
            'email': 'test@gmail.com',
            'password': 'test12345',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
        Test that the password must be more than 5 characters long
        """
        payload = {
            'user': 'test',
            'email': 'test@gmail.com',
            'password': 'tes',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_invalid_credentials(self):
        """
        Test that token is not created if invalid credentials are given
        """
        create_user(username="test", email="test@gmail.com",
                    password="test12345")
        payload = {'email': 'test@gmail.com', 'password': "test123"}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
        Test that token is not created if user doesn't exist
        """
        payload = {'username': 'test',
                   'email': 'test@gmail.com', 'password': 'test12345'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """
        Test that email and password are required
        """
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTests(TestCase):
    """
    Test API requests that require authentication
    """

    def setUp(self):
        self.user = create_user(
            username="test",
            email='test@gmail.com',
            password='test12345',
            first_name='John Doe',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_update_user_profile(self):
        """
        Test updating the user profile for authenticated user
        """
        payload = {'first_name': 'new name', 'password': 'newpassword123'}

        res = self.client.patch(
            reverse('user_details', kwargs={"pk": self.user.id}), payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, payload['first_name'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
