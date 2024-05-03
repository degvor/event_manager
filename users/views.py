from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import User
from django.contrib.auth import authenticate
import jwt, datetime


class UserView(APIView):
    """
    A class-based view to handle creating, updating and deleting users.
    """
    def get(self, request, pk=None):
        if pk:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
            return Response({'user': serializer.data})
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({'users': serializer.data})


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user_saved = serializer.save()
        return Response({"success": "User '{}' created successfully".format(user_saved.id)}, status=201)

    def put(self, request, pk):
        saved_user = User.objects.get(pk=pk)
        serializer = UserSerializer(instance=saved_user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            user_saved = serializer.save()
        return Response({"success": "User '{}' updated successfully".format(user_saved.id)})

    def delete(self, request, pk):
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({"message": "User with id `{}` has been deleted.".format(pk)}, status=204)


class LoginView(APIView):
    """
    A class-based view to handle user login.
    """
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256').decode('UTF-8')
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True, path='/', samesite='None', secure=True)
        response.data = {
            'jwt': token
        }
        return response


class LogoutView(APIView):
    """
    A class-based view to handle user logout.
    """
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
