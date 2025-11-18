from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    RefreshTokenView, CurrentUserView,
    verify_email, ResendVerificationEmailView,
    ForgotPasswordView, ResetPasswordView,
    ChangePasswordView,
    RequestEmailChangeView, VerifyEmailChangeView,
    DeleteAccountView,
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    # User info
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    
    # Email verification
    path('verify-email/', verify_email, name='verify_email'),
    path('resend-email-verification/', ResendVerificationEmailView.as_view(), name='resend_email_verification'),
    
    # Password management
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Email change
    path('request-email-change/', RequestEmailChangeView.as_view(), name='request_email_change'),
    path('verify-email-change/', VerifyEmailChangeView.as_view(), name='verify_email_change'),
]