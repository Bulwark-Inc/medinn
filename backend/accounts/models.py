from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
import random
import string

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, is_seller=False, **extra_fields):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        first_name = extra_fields.pop('first_name', '')
        last_name = extra_fields.pop('last_name', '')

        # Auto-generate username
        base_username = (first_name + last_name).lower().replace(' ', '')
        username = self.generate_unique_username(base_username)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,
            is_seller=is_seller,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, is_seller=False, **extra_fields)

    def generate_unique_username(self, base_username):
        from django.utils.text import slugify
        username = slugify(base_username)
        UserModel = self.model
        while UserModel.objects.filter(username=username).exists():
            suffix = ''.join(random.choices(string.digits, k=4))
            username = slugify(f"{base_username}-{suffix}")
        return username


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_seller = models.BooleanField(default=False) 
    email_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
    date_joined = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return self.email

    def soft_delete(self):
        """Soft delete the user account"""
        self.is_deleted = True
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class AuditLog(models.Model):
    """Track security-related events"""
    EVENT_TYPES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('password_changed', 'Password Changed'),
        ('email_changed', 'Email Changed'),
        ('email_verified', 'Email Verified'),
        ('password_reset_requested', 'Password Reset Requested'),
        ('password_reset_completed', 'Password Reset Completed'),
        ('account_deleted', 'Account Deleted'),
    ]

    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='audit_logs',
        null=True,
        blank=True
    )
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else 'Unknown'
        return f"{user_email} - {self.event_type} at {self.timestamp}"


class PendingEmailChange(models.Model):
    """Track email change requests that need verification"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='pending_email_change')
    new_email = models.EmailField()
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.user.email} -> {self.new_email}"

    def is_expired(self):
        return timezone.now() > self.expires_at