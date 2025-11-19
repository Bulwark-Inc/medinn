from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, Address, NotificationPreference, SellerProfile
from datetime import date

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    completion_percentage = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = (
            'id', 'user_email', 'user_name', 'phone_number', 
            'date_of_birth', 'bio', 'avatar', 'avatar_url',
            'completion_percentage', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_completion_percentage(self, obj):
        return obj.get_completion_percentage()

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

    def validate_date_of_birth(self, value):
        """Ensure user is at least 13 years old"""
        if value:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 13:
                raise serializers.ValidationError("You must be at least 13 years old.")
        return value


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user addresses"""
    
    class Meta:
        model = Address
        fields = (
            'id', 'address_type', 'is_default', 'full_name', 'phone_number',
            'street_address', 'apartment', 'city', 'state', 'postal_code',
            'country', 'delivery_instructions', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, data):
        """Check address limit on creation"""
        request = self.context.get('request')
        if request and not self.instance:  # Creating new address
            user = request.user
            if Address.objects.filter(user=user).count() >= 5:
                raise serializers.ValidationError(
                    "You can only have a maximum of 5 saved addresses. Please delete one before adding a new address."
                )
        return data


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = NotificationPreference
        fields = (
            'id', 'order_updates', 'promotions', 'product_restocked',
            'newsletter', 'seller_updates', 'new_orders', 'low_stock_alerts',
            'updated_at'
        )
        read_only_fields = ('id', 'updated_at')

    def validate(self, data):
        """Hide seller-specific fields from non-sellers"""
        request = self.context.get('request')
        if request and not request.user.is_seller:
            # Remove seller-specific fields if user is not a seller
            seller_fields = ['seller_updates', 'new_orders', 'low_stock_alerts']
            for field in seller_fields:
                data.pop(field, None)
        return data


class SellerProfileSerializer(serializers.ModelSerializer):
    """Serializer for seller profile"""
    user_email = serializers.EmailField(source='user.email', read_only=True)
    store_logo_url = serializers.SerializerMethodField()
    store_banner_url = serializers.SerializerMethodField()
    total_products = serializers.SerializerMethodField()
    
    class Meta:
        model = SellerProfile
        fields = (
            'id', 'user_email', 'store_name', 'store_slug', 'store_description',
            'store_logo', 'store_logo_url', 'store_banner', 'store_banner_url',
            'return_policy', 'shipping_policy', 'is_active', 'total_products',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'store_slug', 'created_at', 'updated_at')

    def get_store_logo_url(self, obj):
        if obj.store_logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.store_logo.url)
            return obj.store_logo.url
        return None

    def get_store_banner_url(self, obj):
        if obj.store_banner:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.store_banner.url)
            return obj.store_banner.url
        return None

    def get_total_products(self, obj):
        """Get total number of products for this seller"""
        return obj.user.products.filter(is_active=True).count() if hasattr(obj.user, 'products') else 0

    def validate_store_name(self, value):
        """Ensure store name is unique"""
        if self.instance:
            if SellerProfile.objects.filter(store_name=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("A store with this name already exists.")
        else:
            if SellerProfile.objects.filter(store_name=value).exists():
                raise serializers.ValidationError("A store with this name already exists.")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Combined serializer with user and profile data"""
    profile = ProfileSerializer(read_only=True)
    notification_preferences = NotificationPreferenceSerializer(read_only=True)
    seller_profile = SellerProfileSerializer(read_only=True)
    addresses_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_seller', 'email_verified', 'date_joined',
            'profile', 'notification_preferences', 'seller_profile',
            'addresses_count'
        )
        read_only_fields = fields

    def get_addresses_count(self, obj):
        return obj.addresses.count()


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    # Common stats
    profile_completion = serializers.IntegerField()
    total_addresses = serializers.IntegerField()
    email_verified = serializers.BooleanField()
    account_age_days = serializers.IntegerField()
    
    # Buyer stats
    total_orders = serializers.IntegerField(required=False)
    pending_orders = serializers.IntegerField(required=False)
    total_spent = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    # Seller stats
    total_products = serializers.IntegerField(required=False)
    active_products = serializers.IntegerField(required=False)
    total_sales = serializers.IntegerField(required=False)
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)