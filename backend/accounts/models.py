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
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # username is auto-created

    objects = UserManager()

    def __str__(self):
        return self.email
