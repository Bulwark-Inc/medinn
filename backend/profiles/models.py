from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    """User profile with personal information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Profile for {self.user.email}"

    def get_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = {
            'avatar': 20,
            'phone_number': 20,
            'bio': 20,
            'date_of_birth': 20,
            'addresses': 20,  # Has at least one address
        }
        
        completed = 0
        
        if self.avatar:
            completed += fields['avatar']
        if self.phone_number:
            completed += fields['phone_number']
        if self.bio:
            completed += fields['bio']
        if self.date_of_birth:
            completed += fields['date_of_birth']
        if self.user.addresses.filter(is_default=True).exists():
            completed += fields['addresses']
        
        return completed

    def save(self, *args, **kwargs):
        # Resize avatar if needed (will be handled in views)
        super().save(*args, **kwargs)


class Address(models.Model):
    """User address for shipping/billing"""
    ADDRESS_TYPES = [
        ('shipping', 'Shipping'),
        ('billing', 'Billing'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPES, default='shipping')
    is_default = models.BooleanField(default=False)
    
    # Address details
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )
    street_address = models.CharField(max_length=255)
    apartment = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Nigeria')
    
    # Optional notes
    delivery_instructions = models.TextField(max_length=500, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Addresses'
        indexes = [
            models.Index(fields=['user', 'is_default']),
            models.Index(fields=['user', 'address_type']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.city}, {self.state}"

    def clean(self):
        """Validate that user doesn't exceed address limit"""
        if not self.pk:  # Only check on creation
            user_addresses_count = Address.objects.filter(user=self.user).count()
            if user_addresses_count >= 5:
                raise ValidationError("You can only have a maximum of 5 saved addresses.")

    def save(self, *args, **kwargs):
        # If this address is set as default, unset other defaults of same type
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        # If this is the user's first address, make it default
        if not self.pk and not Address.objects.filter(user=self.user, address_type=self.address_type).exists():
            self.is_default = True
        
        super().save(*args, **kwargs)


class NotificationPreference(models.Model):
    """User notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email notification settings
    order_updates = models.BooleanField(default=True, help_text="Receive updates about your orders")
    promotions = models.BooleanField(default=True, help_text="Receive promotional emails and offers")
    product_restocked = models.BooleanField(default=True, help_text="Get notified when out-of-stock products are back")
    newsletter = models.BooleanField(default=False, help_text="Subscribe to our newsletter")
    
    # Seller-specific notifications
    seller_updates = models.BooleanField(default=True, help_text="Receive updates about your store (for sellers)")
    new_orders = models.BooleanField(default=True, help_text="Get notified of new orders (for sellers)")
    low_stock_alerts = models.BooleanField(default=True, help_text="Alert when product stock is low (for sellers)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Notification Preferences'

    def __str__(self):
        return f"Notification preferences for {self.user.email}"


class SellerProfile(models.Model):
    """Additional profile information for sellers"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    
    # Store information
    store_name = models.CharField(max_length=255, unique=True)
    store_slug = models.SlugField(max_length=255, unique=True, blank=True)
    store_description = models.TextField(max_length=1000, blank=True)
    store_logo = models.ImageField(upload_to='stores/logos/%Y/%m/', null=True, blank=True)
    store_banner = models.ImageField(upload_to='stores/banners/%Y/%m/', null=True, blank=True)
    
    # Policies
    return_policy = models.TextField(max_length=2000, blank=True)
    shipping_policy = models.TextField(max_length=2000, blank=True)
    
    # Store status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store_slug']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        # Auto-generate slug from store name if not provided
        if not self.store_slug:
            from django.utils.text import slugify
            base_slug = slugify(self.store_name)
            slug = base_slug
            counter = 1
            
            while SellerProfile.objects.filter(store_slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.store_slug = slug
        
        super().save(*args, **kwargs)


class ProfileAuditLog(models.Model):
    """Track profile-related changes"""
    EVENT_TYPES = [
        ('profile_created', 'Profile Created'),
        ('profile_updated', 'Profile Updated'),
        ('avatar_changed', 'Avatar Changed'),
        ('address_added', 'Address Added'),
        ('address_updated', 'Address Updated'),
        ('address_deleted', 'Address Deleted'),
        ('seller_profile_created', 'Seller Profile Created'),
        ('seller_profile_updated', 'Seller Profile Updated'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile_audit_logs')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.event_type} at {self.timestamp}"