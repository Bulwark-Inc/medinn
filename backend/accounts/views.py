from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone

from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ChangeEmailSerializer, ChangePasswordSerializer
)
from .utils import (
    generate_email_token, verify_email_token,
    generate_password_reset_token, verify_password_reset_token,
    generate_email_change_token, verify_email_change_token,
    send_verification_email, send_email_verified_notification,
    send_password_changed_notification, send_email_change_verification,
    send_email_changed_notification, log_audit_event, cleanup_old_audit_logs
)
from .throttles import (
    LoginRateThrottle, PasswordResetRateThrottle,
    EmailVerificationRateThrottle, RegisterRateThrottle
)
from .models import PendingEmailChange

User = get_user_model()


# ========== Helper Functions ==========

def set_refresh_cookie(response, refresh_token):
    """Set refresh token in httpOnly cookie"""
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        max_age=60 * 60 * 24 * 7  # 7 days
    )


def clear_refresh_cookie(response):
    """Clear the refresh token cookie"""
    response.delete_cookie('refresh_token')


# =====x===== Helper Functions =====x=====


# ========== Register, Login, Refresh, Logout ==========

class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [RegisterRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Send verification email
            try:
                send_verification_email(user)
            except Exception as e:
                print(f"Failed to send verification email: {e}")

            # Log the registration
            log_audit_event('login_success', user=user, request=request)

            response = Response({
                'access': access_token,
                'user': UserSerializer(user).data,
                'message': 'User registered successfully. Please check your email to verify your account.'
            }, status=status.HTTP_201_CREATED)

            set_refresh_cookie(response, str(refresh))
            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Log successful login
            log_audit_event('login_success', user=user, request=request)
            cleanup_old_audit_logs(user)

            response = Response({
                'access': access_token,
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            }, status=status.HTTP_200_OK)

            set_refresh_cookie(response, str(refresh))
            return response

        # Log failed login attempt
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_deleted=False)
            log_audit_event('login_failed', user=user, request=request, details={'reason': 'invalid_credentials'})
        except User.DoesNotExist:
            log_audit_event('login_failed', request=request, details={'email': email, 'reason': 'user_not_found'})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response({'detail': 'Refresh token missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            return Response({'access': access_token}, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return Response({'detail': 'Invalid or expired refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)
        return response


# =====x===== Register, Login, Refresh, Logout =====x=====


# ========== Email Verification ==========

@api_view(['POST'])
def verify_email(request):
    token = request.data.get('token')
    email = verify_email_token(token)
    
    if email is None:
        return Response({'detail': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(email=email, is_deleted=False)
        
        if user.email_verified:
            return Response({'message': 'Email is already verified'}, status=status.HTTP_200_OK)
        
        user.email_verified = True
        user.save()

        # Send confirmation email
        try:
            send_email_verified_notification(user)
        except Exception as e:
            print(f"Failed to send verification confirmation: {e}")

        # Log the event
        log_audit_event('email_verified', user=user, request=request)

        return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ResendVerificationEmailView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [EmailVerificationRateThrottle]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_deleted=False)
            
            if user.email_verified:
                return Response({"detail": "Email is already verified."}, status=status.HTTP_400_BAD_REQUEST)

            send_verification_email(user)
            return Response({"message": "Verification email resent successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# =====x===== Email Verification =====x=====


# ========== Password Reset ==========

class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_deleted=False)
            token = generate_password_reset_token(user.email)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"

            subject = "Password Reset Request"
            message = f"""Hi {user.first_name},

You requested to reset your password. Click the link below to reset it:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The MedInn Team
"""
            from django.core.mail import send_mail
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            # Log the event
            log_audit_event('password_reset_requested', user=user, request=request)

            return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            # Don't reveal if user exists or not
            return Response({"message": "If an account exists with this email, a password reset link has been sent."}, status=status.HTTP_200_OK)


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
            user = User.objects.get(email=email, is_deleted=False)
            
            # Validate password strength
            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return Response({"detail": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            # Send confirmation email
            try:
                send_password_changed_notification(user)
            except Exception as e:
                print(f"Failed to send password change notification: {e}")

            # Log the event
            log_audit_event('password_reset_completed', user=user, request=request)

            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)


# =====x===== Password Reset =====x=====


# ========== Password Change (Authenticated) ==========

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            # Send confirmation email
            try:
                send_password_changed_notification(user)
            except Exception as e:
                print(f"Failed to send password change notification: {e}")

            # Log the event
            log_audit_event('password_changed', user=user, request=request)

            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====x===== Password Change =====x=====


# ========== Email Change ==========

class RequestEmailChangeView(APIView):
    """Request to change email - sends verification to new email"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangeEmailSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            new_email = serializer.validated_data['new_email']
            
            # Generate token
            token = generate_email_change_token(new_email)
            
            # Store pending email change
            PendingEmailChange.objects.filter(user=user).delete()  # Remove any existing pending changes
            PendingEmailChange.objects.create(
                user=user,
                new_email=new_email,
                token=token,
                expires_at=timezone.now() + timezone.timedelta(hours=1)
            )
            
            # Send verification email to new address
            try:
                send_email_change_verification(user, new_email, token)
            except Exception as e:
                print(f"Failed to send email change verification: {e}")
                return Response({"detail": "Failed to send verification email."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"message": f"Verification email sent to {new_email}."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailChangeView(APIView):
    """Verify the new email and complete the change"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pending_change = PendingEmailChange.objects.get(token=token)
            
            if pending_change.is_expired():
                pending_change.delete()
                return Response({"detail": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

            # Verify token
            new_email = verify_email_change_token(token)
            if new_email is None or new_email != pending_change.new_email:
                return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if new email is still available
            if User.objects.filter(email=new_email, is_deleted=False).exists():
                pending_change.delete()
                return Response({"detail": "This email is already in use."}, status=status.HTTP_400_BAD_REQUEST)

            # Update email
            user = pending_change.user
            old_email = user.email
            user.email = new_email
            user.email_verified = True  # Auto-verify the new email
            user.save()

            # Send notification to old email
            try:
                send_email_changed_notification(user, old_email)
            except Exception as e:
                print(f"Failed to send email change notification: {e}")

            # Log the event
            log_audit_event('email_changed', user=user, request=request, details={'old_email': old_email, 'new_email': new_email})

            # Delete pending change
            pending_change.delete()

            return Response({"message": "Email changed successfully."}, status=status.HTTP_200_OK)

        except PendingEmailChange.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


# =====x===== Email Change =====x=====


# ========== User Management ==========

class CurrentUserView(APIView):
    """Get current authenticated user details"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class DeleteAccountView(APIView):
    """Soft delete user account"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password')
        
        if not password:
            return Response({"detail": "Password is required to delete account."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        
        # Verify password
        if not user.check_password(password):
            return Response({"detail": "Invalid password."}, status=status.HTTP_400_BAD_REQUEST)

        # Soft delete
        user.soft_delete()

        # Log the event
        log_audit_event('account_deleted', user=user, request=request)

        # Clear session
        response = Response({"message": "Account deleted successfully."}, status=status.HTTP_200_OK)
        clear_refresh_cookie(response)

        return response


# =====x===== User Management =====x=====