from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, LoginSerializer
from django.core.mail import send_mail
from .utils import generate_email_token, verify_email_token, generate_password_reset_token, verify_password_reset_token
from django.conf import settings

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

User = get_user_model()


# ========== Helper Functions ==========

# Helper to set refresh token cookie
def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax'
    )

# Helper to clear the cookie
def clear_refresh_cookie(response):
    response.delete_cookie('refresh_token')

# Helper to send verification email
def send_verification_email(user):
    token = generate_email_token(user.email)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    subject = "Verify your email"
    message = f"Hi {user.email},\n\nClick the link to verify your email:\n{verify_url}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

# =====x===== Helper Functions =====x=====


# ========== Register, Login, Refresh, Logout ==========

# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                'access': access_token,
                'message': 'User registered successfully'
            }, status=status.HTTP_201_CREATED)

            set_refresh_cookie(response, str(refresh))
            send_verification_email(user)
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login View
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            response = Response({
                'access': access_token,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)

            set_refresh_cookie(response, str(refresh))
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]  # This endpoint is open to everyone

    def post(self, request):
        # Get the refresh token from cookies
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'detail': 'Refresh token missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Attempt to validate the refresh token
            refresh = RefreshToken(refresh_token)
            # Generate a new access token from the refresh token
            access_token = str(refresh.access_token)

            # Return the new access token in the response
            return Response({'access': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            # If there's an issue with the refresh token, return an error
            print(f"Error refreshing token: {e}")
            return Response({'detail': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

# Logout View (clears refresh token cookie)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # Optional: handle invalid/missing token

        response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)
        return response

# =====x===== Register, Refresh Login, Logout =====x=====


# ========== Email and password ==========

@api_view(['POST'])
def verify_email(request):
    token = request.data.get('token')
    email = verify_email_token(token)
    if email is None:
        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email)
        user.email_verified = True
        user.save()
        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            if user.email_verified:
                return Response({"detail": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            send_verification_email(user)
            return Response({"detail": "Verification email resent successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# Request reset Forgotten password
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            token = generate_password_reset_token(user.email)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

            subject = "Password Reset Request"
            message = f"Hi {user.email},\n\nClick the link to reset your password:\n{reset_url}"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            return Response({"detail": "Password reset email sent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# Reset New Password
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response({"detail": "Token and new password are required."}, status=status.HTTP_400_BAD_REQUEST)

        email = verify_password_reset_token(token)
        if email is None:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password reset successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# =====x===== Email and password =====x=====


# Get current authenticated user
class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'email': user.email,
            'username': user.username,
            'email_verified': user.email_verified,
        })