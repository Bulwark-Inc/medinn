from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView,
    RefreshTokenView, CurrentUserView,
    verify_email, ResendVerificationEmailView,
    ForgotPasswordView, ResetPasswordView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    path('verify-email/', verify_email, name='verify-email'),
    path('resend-email-verification/', ResendVerificationEmailView.as_view(), name='resend-email-verification'),

    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]
