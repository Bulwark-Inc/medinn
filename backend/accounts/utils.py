from itsdangerous import URLSafeTimedSerializer
from django.conf import settings

def generate_email_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='email-confirm')

def verify_email_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
        return email
    except Exception:
        return None

def generate_password_reset_token(email):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt='password-reset')

def verify_password_reset_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt='password-reset', max_age=expiration)
        return email
    except Exception:
        return None