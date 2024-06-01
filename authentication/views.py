from decouple import config
from django.contrib.auth import authenticate
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from utils.data_generators import generate_password, generate_username

from .models import User
from .serializers import SignupSerializer, UserSerializer


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "authUser": UserSerializer(user).data,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(email=email, password=password)
        if user is None:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "authUser": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LoginWithGoogleView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data["credential"]
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), config('GOOGLE_CLIENT_ID'))
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        email = idinfo['email']
        first_name = idinfo['given_name']
        last_name = idinfo['family_name']

        user = User.objects.filter(email=email).first()
        # if the user exists then login the user and mark the user as verified
        if user:
            if not user.is_verified:
                user.is_verified = True
                user.save()
            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            user_data = UserSerializer(user).data
            response_data = {
                "authUser": user_data,
                "refresh_token": refresh_token,
                "access_token": access_token,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            user = User.objects.create(
                username=generate_username(first_name=first_name, last_name=last_name),
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=generate_password(),
                is_verified=True,
            )

            token = RefreshToken.for_user(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            user_data = UserSerializer(user).data

            response_data = {
                "authUser": user_data,
                "refresh_token": refresh_token,
                "access_token": access_token,
            }
            return Response(response_data, status=status.HTTP_200_OK)
