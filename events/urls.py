from django.urls import path
from .views import EventView, RegisterForEventView, api_search_events

urlpatterns = [
    path('event', EventView.as_view(), name='events-list'),
    path('event/<int:pk>/', EventView.as_view(), name='event-detail'),
    path('register/<int:pk>/', RegisterForEventView.as_view(), name='register-for-event'),
    path('register-cancel/<int:pk>/', RegisterForEventView.as_view(), name='cancel-register-for-event'),
    path('search/', api_search_events, name='api_search_events'),
]
