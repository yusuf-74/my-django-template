from decouple import config
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from utils.data_generators import generate_password, generate_username

from .models import User
from .serializers import SignupSerializer, UserSerializer
from .tasks import send_email

REACT_VERIFY_EMAIL_URL = config("REACT_VERIFY_EMAIL_URL", default="dummy")
REACT_RESET_PASSWORD_URL = config("REACT_RESET_PASSWORD_URL", default="dummy")


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # create a token to verify the email
            token = RefreshToken.for_user(user)
            context = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "reset_password_url": REACT_RESET_PASSWORD_URL + f"?token={token}",
                'platform_name': "Ashour's CodeCrafts",
                "logo_url": 'https://dl6w6xzg21289.cloudfront.net/public/media/media_data/Screenshot+2024-06-01+224302.png',
            }
            body = render_to_string("mails/reset_password.html", context)
            sender = config("EMAIL_HOST_USER")
            recipient = [user.email]
            subject = "Verify your email"
            send_email.delay(sender, recipient, subject, body)

            return Response(status=status.HTTP_201_CREATED)
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
        if not user.is_verified:
            return Response({"error": "Email is not verified"}, status=status.HTTP_400_BAD_REQUEST)
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


class VerifyEmailView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        try:
            token = RefreshToken(token)
            user = User.objects.get(id=token.payload["user_id"])
            user.is_verified = True
            user.save()
            data = UserSerializer(user).data
            return Response(
                {
                    "authUser": data,
                    "refresh": str(token),
                    "access": str(token.access_token),
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            token = RefreshToken.for_user(user)
            context = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "reset_password_url": REACT_RESET_PASSWORD_URL + f"?token={token}",
                'platform_name': "Ashour's CodeCrafts",
                "logo_url": 'https://dl6w6xzg21289.cloudfront.net/public/media/media_data/Screenshot+2024-06-01+224302.png',
            }
            body = render_to_string("mails/reset_password.html", context)
            sender = config("EMAIL_HOST_USER")
            recipient = [user.email]
            subject = "Reset your password"
            send_email.delay(sender, recipient, subject, body)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get("password")
        repeat_password = request.data.get("repeat_password")
        if password != repeat_password:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=request.user.id)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
