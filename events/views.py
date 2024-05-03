from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EventSerializer
from .models import Event, RegistrationForEvent
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from users.models import User
from django.core.mail import send_mail
from datetime import datetime
from django.http import JsonResponse
from django.db.models import Q


def send_registration_email(user, event):
    """
    Sends an email to `user` notifying them of their registration to `event`.
    Not using this function in code.
    """
    subject = 'Event Registration Confirmation'
    message = f'Hi {user.first_name},\n\nYou have successfully registered for {event.title}. We look forward to seeing you there!\n\nBest regards,\nEvent Management Team'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]

    send_mail(
        subject,
        message,
        email_from,
        recipient_list,
        fail_silently=False,
    )


def get_user_from_token(request):
    """
    Extracts the user from the JWT token in the request's cookies.
    """
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


def api_search_events(request):
    """
    Searches for events based on the query, date_from, and date_to parameters.
    """
    query = request.GET.get('query', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    events = Event.objects.all()

    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            events = events.filter(date__gte=date_from)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format for "date_from". Please use YYYY-MM-DD format.'}, status=400)

    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            events = events.filter(date__lte=date_to)
        except ValueError:
            return JsonResponse({'error': 'Invalid date format for "date_to". Please use YYYY-MM-DD format.'}, status=400)

    data = list(events.values('title', 'description', 'date', 'location'))
    return JsonResponse(data, safe=False)


class EventView(APIView):
    """
    A view that handles GET, POST, PUT, and DELETE requests for events.
    """
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
    """
    A view that handles POST and DELETE requests for registering/unregistering for events.
    """
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
