from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer
from .models import Event, RegistrationForEvent
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from users.models import User


def get_user_from_token(request):
    token = request.COOKIES.get('jwt')
    if not token:
        raise AuthenticationFailed('Unauthenticated!')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated!')

    user = User.objects.filter(id=payload['id']).first()
    if user is None:
        raise AuthenticationFailed('User not found!')

    return user


class EventView(APIView):
    def get(self, request, pk=None):
        if pk:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event)
            return Response({'event': serializer.data})
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response({'events': serializer.data})


    def post(self, request):
        try:
            user = get_user_from_token(request)
        except AuthenticationFailed as e:
            return Response({'error': str(e)})
        request.data['organizer'] = user.pk
        # event = request.data.get('event')
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            event_saved = serializer.save()
        return Response({"success": "Event '{}' created successfully".format(event_saved.title)}, status=201)

    def put(self, request, pk):
        try:
            user = get_user_from_token(request)
        except AuthenticationFailed as e:
            return Response({'error': str(e)})

        saved_event = Event.objects.get(pk=pk)
        if saved_event.organizer != user:
            return Response({'error': 'You do not have permission to delete this event.'})
        serializer = EventSerializer(instance=saved_event, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            event_saved = serializer.save()
        return Response({"success": "Event '{}' updated successfully".format(event_saved.title)})

    def delete(self, request, pk):
        try:
            user = get_user_from_token(request)
        except AuthenticationFailed as e:
            return Response({'error': str(e)})

        event = Event.objects.get(pk=pk)

        if event.organizer != user:
            return Response({'error': 'You do not have permission to delete this event.'})

        event.delete()
        return Response({'message': f"Event with id `{pk}` has been deleted."}, status=204)


class RegisterForEventView(APIView):
    def post(self, request, pk):
        try:
            user = get_user_from_token(request)
        except AuthenticationFailed as e:
            return Response({'error': str(e)})

        event = Event.objects.get(pk=pk)

        if RegistrationForEvent.objects.filter(user=user, event=event).exists():
            return Response({'message': 'You are already registered for this event.'})

        RegistrationForEvent.objects.create(user=user, event=event)
        return Response({'message': f'You have registered for {event.title}.'})

    def delete(self, request, pk):
        try:
            user = get_user_from_token(request)
        except AuthenticationFailed as e:
            return Response({'error': str(e)})

        event = Event.objects.get(pk=pk)

        registration = RegistrationForEvent.objects.filter(user=user, event=event)
        if not registration.exists():
            return Response({'message': 'You are not registered for this event.'})
        registration.delete()
        return Response({'message': f'You have unregistered from {event.title}.'})
