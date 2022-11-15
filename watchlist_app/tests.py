from django.contrib.auth.models import User
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .api import serializers
from . import models


class StreamPlatformTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='Test', password='Password@123')
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.stream = models.StreamPlatform.objects.create(name='Test', about='Test description', website='https://test.com')

    def test_stream_platform_create(self):
        data = {
            'name': 'HBO',
            'about': 'Test description',
            'website': 'https://test.com'
        }
        response = self.client.post(reverse('stream_platform-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stream_platform_list(self):
        response = self.client.get(reverse('stream_platform-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stream_platform_ind(self):
        response = self.client.get(reverse('stream_platform-detail', args=(self.stream.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stream_platform_update(self):
        data = {
            'name': 'HBO',
            'about': 'Test description',
            'website': 'https://test.com'
        }
        response = self.client.put(reverse('stream_platform-detail', args=(self.stream.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_stream_platform_delete(self):
        response = self.client.delete(reverse('stream_platform-detail', args=(self.stream.id,)))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WatchListTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='Test', password='Password@123')
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.stream = models.StreamPlatform.objects.create(name='Test', about='Test description',
                                                           website='https://test.com')
        self.watch_list = models.WatchList.objects.create(platform=self.stream, title='Test title',
                                                          storyline='Test story', active=True)

    def test_watch_list_create(self):
        data = {
            'platform': self.stream,
            'title': 'Test title',
            'storyline': 'Test story',
            'active': True
        }
        response = self.client.post(reverse('movie_list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_watch_list_lst(self):
        response = self.client.get(reverse('movie_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_watch_list_ind(self):
        response = self.client.get(reverse('movie_detail', args=(self.watch_list.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(models.WatchList.objects.count(), 1)
        self.assertEqual(models.WatchList.objects.get().title, 'Test title')

    def test_watch_list_update(self):
        data = {
            'platform': self.stream,
            'title': 'Test title changed',
            'storyline': 'Test story changed',
            'active': False
        }
        response = self.client.put(reverse('movie_detail', args=(self.watch_list.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_watch_list_delete(self):
        response = self.client.delete(reverse('movie_detail', args=(self.watch_list.id,)))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ReviewTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='Test', password='Password@123')
        self.token = Token.objects.get(user__username=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.stream = models.StreamPlatform.objects.create(name='Test', about='Test description',
                                                           website='https://test.com')
        self.watch_list = models.WatchList.objects.create(platform=self.stream, title='Test title',
                                                          storyline='Test story', active=True)
        self.watch_list2 = models.WatchList.objects.create(platform=self.stream, title='Test title 2',
                                                          storyline='Test story 2', active=True)
        self.review = models.Review.objects.create(author=self.user, rating=5, description='Some descr',
                                                   watchlist=self.watch_list2, active=True)
        self.data = {
            'author': self.user,
            'rating': 5,
            'description': "Test description",
            'watchlist': self.watch_list,
            'active': True
        }

    def test_review_create(self):
        response1 = self.client.post(reverse('review_create', args=(self.watch_list.id,)), self.data)
        response2 = self.client.post(reverse('review_create', args=(self.watch_list.id,)), self.data)
        self.assertEqual(models.Review.objects.count(), 2)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_create_unauth(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(reverse('review_create', args=(self.watch_list.id,)), self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update(self):
        data = {
            'author': self.user,
            'rating': 4,
            'description': "Test description updated",
            'watchlist': self.watch_list2,
            'active': False
        }
        response = self.client.put(reverse('review_detail', args=(self.review.id,)), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_list(self):
        response = self.client.get(reverse('review_list', args=(self.watch_list.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_ind(self):
        response = self.client.get(reverse('review_detail', args=(self.review.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
