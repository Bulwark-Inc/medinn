from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
from .models import ProfileAuditLog


def resize_image(image, max_size=(300, 300), quality=85):
    """
    Resize and compress an image
    
    Args:
        image: ImageField or uploaded file
        max_size: tuple of (width, height) for maximum dimensions
        quality: JPEG quality (1-100)
    
    Returns:
        InMemoryUploadedFile: Processed image
    """
    try:
        img = Image.open(image)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize maintaining aspect ratio
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        # Create InMemoryUploadedFile
        return InMemoryUploadedFile(
            output,
            'ImageField',
            f"{image.name.split('.')[0]}.jpg",
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
    except Exception as e:
        print(f"Error resizing image: {e}")
        return image


def resize_avatar(image):
    """Resize avatar to 300x300"""
    return resize_image(image, max_size=(300, 300), quality=85)


def resize_store_logo(image):
    """Resize store logo to 200x200"""
    return resize_image(image, max_size=(200, 200), quality=90)


def resize_store_banner(image):
    """Resize store banner to 1200x400"""
    return resize_image(image, max_size=(1200, 400), quality=90)


def log_profile_event(user, event_type, details=None):
    """
    Create a profile audit log entry
    
    Args:
        user: User object
        event_type: Type of event (see ProfileAuditLog.EVENT_TYPES)
        details: Additional details as dictionary
    """
    ProfileAuditLog.objects.create(
        user=user,
        event_type=event_type,
        details=details or {}
    )


def validate_image_file(file):
    """
    Validate uploaded image file
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Check file size (max 2MB)
    if file.size > 2 * 1024 * 1024:
        return False, "Image file size cannot exceed 2MB."
    
    # Check file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        return False, "Only JPEG, PNG, and WebP images are allowed."
    
    try:
        # Try to open and verify it's a valid image
        img = Image.open(file)
        img.verify()
        return True, None
    except Exception:
        return False, "Invalid image file."


def get_dashboard_stats(user):
    """
    Calculate dashboard statistics for a user
    
    Args:
        user: User object
    
    Returns:
        dict: Dashboard statistics
    """
    from datetime import datetime
    from django.db.models import Sum, Count, Q
    
    # Common stats
    stats = {
        'profile_completion': user.profile.get_completion_percentage(),
        'total_addresses': user.addresses.count(),
        'email_verified': user.email_verified,
        'account_age_days': (datetime.now().date() - user.date_joined.date()).days,
    }
    
    # Buyer stats (orders will be calculated when orders app is ready)
    if hasattr(user, 'orders'):
        orders = user.orders.all()
        stats['total_orders'] = orders.count()
        stats['pending_orders'] = orders.filter(status='pending').count()
        stats['total_spent'] = orders.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
    else:
        stats['total_orders'] = 0
        stats['pending_orders'] = 0
        stats['total_spent'] = 0
    
    # Seller stats
    if user.is_seller:
        if hasattr(user, 'products'):
            products = user.products.all()
            stats['total_products'] = products.count()
            stats['active_products'] = products.filter(is_active=True).count()
        else:
            stats['total_products'] = 0
            stats['active_products'] = 0
        
        # Sales stats (will be calculated when orders app is ready)
        if hasattr(user, 'seller_orders'):
            seller_orders = user.seller_orders.all()
            stats['total_sales'] = seller_orders.count()
            stats['total_revenue'] = seller_orders.filter(status='completed').aggregate(
                total=Sum('total_amount')
            )['total'] or 0
        else:
            stats['total_sales'] = 0
            stats['total_revenue'] = 0
    
    return stats


def get_recent_orders(user, limit=5):
    """
    Get recent orders for a user
    
    Args:
        user: User object
        limit: Number of orders to retrieve
    
    Returns:
        QuerySet: Recent orders
    """
    if hasattr(user, 'orders'):
        return user.orders.all().order_by('-created_at')[:limit]
    return []


def get_recent_seller_orders(user, limit=5):
    """
    Get recent orders for a seller
    
    Args:
        user: User object (must be a seller)
        limit: Number of orders to retrieve
    
    Returns:
        QuerySet: Recent seller orders
    """
    if user.is_seller and hasattr(user, 'seller_orders'):
        return user.seller_orders.all().order_by('-created_at')[:limit]
    return []