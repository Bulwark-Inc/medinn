from itsdangerous import URLSafeTimedSerializer
from django.conf import settings
from django.core.mail import send_mail
from .models import AuditLog
from django.utils import timezone


# ========== Token Generation and Verification ==========

def generate_email_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirm')


def verify_email_token(token, expiration=86400):  # 24 hours
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
        return email
    except Exception:
        return None


def generate_password_reset_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='password-reset')


def verify_password_reset_token(token, expiration=3600):  # 1 hour
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
        return email
    except Exception:
        return None


def generate_email_change_token(email):
    """Generate token for email change verification"""
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-change')


def verify_email_change_token(token, expiration=3600):  # 1 hour
    """Verify email change token"""
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-change', max_age=expiration)
        return email
    except Exception:
        return None


# ========== Email Sending Functions ==========

def send_verification_email(user):
    """Send email verification link"""
    token = generate_email_token(user.email)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"

    subject = "Verify your MedInn account"
    message = f"""Hi {user.first_name},

Welcome to MedInn! Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you didn't create this account, please ignore this email.

Best regards,
The MedInn Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_email_verified_notification(user):
    """Send confirmation that email was successfully verified"""
    subject = "Email verified successfully"
    message = f"""Hi {user.first_name},

Your email has been successfully verified! You can now access all features of MedInn.

Best regards,
The MedInn Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_password_changed_notification(user):
    """Send notification that password was changed"""
    subject = "Password changed successfully"
    message = f"""Hi {user.first_name},

Your password has been changed successfully.

If you didn't make this change, please contact our support team immediately.

Best regards,
The MedInn Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])


def send_email_change_verification(user, new_email, token):
    """Send verification email to new email address"""
    verify_url = f"{settings.FRONTEND_URL}/verify-email-change?token={token}"

    subject = "Verify your new email address"
    message = f"""Hi {user.first_name},

You requested to change your email address. Please verify your new email by clicking the link below:

{verify_url}

This link will expire in 1 hour.

If you didn't request this change, please ignore this email.

Best regards,
The MedInn Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [new_email])


def send_email_changed_notification(user, old_email):
    """Notify old email that email was changed"""
    subject = "Email address changed"
    message = f"""Hi {user.first_name},

Your account email address has been changed from {old_email} to {user.email}.

If you didn't make this change, please contact our support team immediately.

Best regards,
The MedInn Team
"""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [old_email])


# ========== Audit Logging ==========

def log_audit_event(event_type, user=None, request=None, details=None):
    """
    Create an audit log entry
    
    Args:
        event_type: Type of event (see AuditLog.EVENT_TYPES)
        user: User object (optional for failed login attempts)
        request: Django request object (to extract IP and user agent)
        details: Additional details as dictionary
    """
    ip_address = None
    user_agent = ''
    
    if request:
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    AuditLog.objects.create(
        user=user,
        event_type=event_type,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {}
    )


def cleanup_old_audit_logs(user, keep_last=100):
    """Keep only the last N audit logs per user"""
    logs = AuditLog.objects.filter(user=user).order_by('-timestamp')
    if logs.count() > keep_last:
        logs_to_delete = logs[keep_last:]
        log_ids = [log.id for log in logs_to_delete]
        AuditLog.objects.filter(id__in=log_ids).delete()


# ========== Helper Functions ==========

def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip