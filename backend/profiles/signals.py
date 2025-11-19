from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile, NotificationPreference, SellerProfile, ProfileAuditLog

User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create Profile and NotificationPreference when a User is created
    """
    if created:
        # Create basic profile
        Profile.objects.create(user=instance)
        
        # Create notification preferences with defaults
        NotificationPreference.objects.create(user=instance)
        
        # If user is a seller, create seller profile
        if instance.is_seller:
            store_name = f"{instance.get_full_name()}'s Store"
            SellerProfile.objects.create(
                user=instance,
                store_name=store_name
            )
        
        # Log profile creation
        ProfileAuditLog.objects.create(
            user=instance,
            event_type='profile_created',
            details={'created_at': str(instance.date_joined)}
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, created, **kwargs):
    """
    Ensure profile exists and create seller profile if user becomes a seller
    """
    if not created:
        # Ensure profile exists
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        
        # Ensure notification preferences exist
        if not hasattr(instance, 'notification_preferences'):
            NotificationPreference.objects.create(user=instance)
        
        # Create seller profile if user is now a seller and doesn't have one
        if instance.is_seller and not hasattr(instance, 'seller_profile'):
            store_name = f"{instance.get_full_name()}'s Store"
            SellerProfile.objects.create(
                user=instance,
                store_name=store_name
            )
            
            ProfileAuditLog.objects.create(
                user=instance,
                event_type='seller_profile_created',
                details={'store_name': store_name}
            )