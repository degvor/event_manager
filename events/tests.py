from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from .models import Event, RegistrationForEvent
from .serializers import EventSerializer
from datetime import datetime
import json

User = get_user_model()


class EventViewTests(APITestCase):
    def setUp(self):

        self.client = APIClient()
        self.login_url = reverse('login')
        self.url_list = reverse('user-list')
        self.client.post(self.url_list, {'name': 'newuser', 'email': 'login1@example.com', 'password': 'loginpassword'})
        self.token = self.client.post(self.login_url, {'email': 'login1@example.com', 'password': 'loginpassword'}).data
        self.user1 = self.client.get(self.url_list, cookies=self.token).data

        self.event = Event.objects.create(
            title="Test Event",
            description="Test Description",
            organizer=User.objects.get(pk=self.user1['users'][0]['id']),
            date=datetime.now()
        )

        self.list_url = reverse('events-list')
        self.detail_url = reverse('event-detail', kwargs={'pk': self.event.pk})


    def test_get_event_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['events']), 1)

    def test_get_event_detail(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['event']['title'], 'Test Event')

    def test_create_event(self):
        data = {'title': 'New Event',
                'description': 'New Event Description',
                'location': 'New Event Location',
                'date': '2024-01-01T00:00:00Z'}
        response = self.client.post(self.list_url, data, format='json', cookies=self.token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 2)

    def test_update_event(self):
        data = {'title': 'Updated Event'}
        response = self.client.put(self.detail_url, data, format='json', cookies=self.token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event')

    def test_delete_event(self):
        data = {'name': 'newuser', 'email': 'login@example.com', 'password': 'loginpassword'}
        self.client.post(self.login_url, data)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)

