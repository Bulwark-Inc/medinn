from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data - used across the app"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'full_name', 'is_seller', 'email_verified', 'date_joined'
        )
        read_only_fields = ('id', 'username', 'email_verified', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_seller', 'password', 'password2')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return data

    def validate_email(self, value):
        """Check if email is already taken"""
        if User.objects.filter(email=value, is_deleted=False).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        # Check if user exists and is not deleted
        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            raise serializers.ValidationError(_("Invalid email or password"))

        # Authenticate
        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError(_("Invalid email or password"))

        if not user.is_active:
            raise serializers.ValidationError(_("Account disabled."))

        if not user.email_verified:
            raise serializers.ValidationError(_("Email is not verified. Please check your inbox."))

        return {'user': user}


class ChangeEmailSerializer(serializers.Serializer):
    """Serializer for email change request"""
    new_email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_new_email(self, value):
        # Check if email is already in use
        if User.objects.filter(email=value, is_deleted=False).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        # Verify password
        if not user.check_password(data['password']):
            raise serializers.ValidationError({"password": "Invalid password."})
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"new_password": "Passwords do not match"})
        return data

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class AuditLogSerializer(serializers.Serializer):
    """Serializer for audit log display"""
    event_type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    ip_address = serializers.IPAddressField()
    details = serializers.JSONField()