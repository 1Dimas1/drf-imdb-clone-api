from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token


class RegistrationTestCases(APITestCase):

    def test_registration(self):
        data = {
            'username': 'testcase',
            'email': 'testcase@xyz.com',
            'password': 'Somepass123.',
            'password2': 'Somepass123.',
        }
        response = self.client.post(reverse('registration'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginLogoutTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='Example', password='Somepass123.')

    def test_login(self):
        data = {
            'username': 'Example',
            'password': 'Somepass123.',
        }
        response = self.client.post(reverse('login'), data)
        self.token = Token.objects.get(user__username=data['username'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.token.key)

    def test_logout(self):
        self.token = Token.objects.get(user__username='Example')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
