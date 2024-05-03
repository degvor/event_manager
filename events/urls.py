from django.urls import path
from .views import EventView, RegisterForEventView

urlpatterns = [
    path('event', EventView.as_view(), name='events-list'),
    path('event/<int:pk>/', EventView.as_view(), name='event-detail'),
    path('register/<int:pk>/', RegisterForEventView.as_view(), name='register-for-event'),
    path('register-cancel/<int:pk>/', RegisterForEventView.as_view(), name='cancel-register-for-event')
]
