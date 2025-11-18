from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """
    Limit login attempts to 5 per 15 minutes
    """
    rate = '5/15m'
    scope = 'login'


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Limit password reset requests to 3 per hour
    """
    rate = '3/hour'
    scope = 'password_reset'


class EmailVerificationRateThrottle(AnonRateThrottle):
    """
    Limit email verification resend to 3 per hour
    """
    rate = '3/hour'
    scope = 'email_verification'


class RegisterRateThrottle(AnonRateThrottle):
    """
    Limit registration attempts to 3 per hour
    """
    rate = '3/hour'
    scope = 'register'