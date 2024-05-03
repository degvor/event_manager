from rest_framework import serializers
from .models import Event, RegistrationForEvent


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class RegistrationForEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationForEvent
        fields = '__all__'

