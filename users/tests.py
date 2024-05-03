from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(name='testuser', email='test@example.com', password='testpassword123')
        self.url_list = reverse('user-list')
        self.url_detail = reverse('user-detail', kwargs={'pk': self.user.pk})

    def test_get_all_users(self):
        """
        Ensure we can retrieve a list of all users.
        """
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['users']), 1)

    def test_get_single_user(self):
        """
        Ensure we can retrieve a single user by pk.
        """
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_create_user(self):
        """
        Ensure we can create a new user.
        """
        data = {'name': 'newuser', 'email': 'new@example.com', 'password': 'newpassword123'}
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_update_user(self):
        """
        Ensure we can update an existing user.
        """
        data = {'name': 'updateduser'}
        response = self.client.put(self.url_detail, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'updateduser')

    def test_delete_user(self):
        """
        Ensure we can delete a user.
        """
        response = self.client.delete(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.url_list = reverse('user-list')

    def test_login(self):
        """
        Ensure we can log in a user and receive a token.
        """

        data = {'name': 'newuser', 'email': 'login@example.com', 'password': 'loginpassword'}
        self.client.post(self.url_list, data)

        data = {'email': 'login@example.com', 'password': 'loginpassword'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('jwt' in response.cookies)

    def test_logout(self):
        """
        Ensure we can log out a user and clear the token.
        """

        data = {'name': 'newuser', 'email': 'login@example.com', 'password': 'loginpassword'}
        self.client.post(self.url_list, data)

        data = {'email': 'login@example.com', 'password': 'loginpassword'}
        self.client.post(self.login_url, data)

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies['jwt'].value, '')
