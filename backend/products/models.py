from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
import os

User = get_user_model()


# =========================
# CATEGORY MODEL
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='subcategories',
        null=True,
        blank=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name


# =========================
# PRODUCT MODEL
# =========================
class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name', unique_with='seller', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'is_active', 'is_deleted']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['slug']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.price <= 0:
            raise ValidationError("Price must be greater than 0")
        if self.low_stock_threshold < 0:
            raise ValidationError("Low stock threshold cannot be negative")

    def save(self, *args, **kwargs):
        # Auto-deactivate if out of stock
        if self.stock == 0:
            self.is_active = False
        super().save(*args, **kwargs)

    @property
    def is_low_stock(self):
        """Check if product stock is below threshold"""
        return self.stock > 0 and self.stock <= self.low_stock_threshold

    @property
    def is_available(self):
        """Check if product is available for purchase"""
        return self.is_active and not self.is_deleted and self.stock > 0


# =========================
# PRODUCT IMAGE MODEL
# =========================
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='products/images/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-is_primary', 'created_at']
        indexes = [
            models.Index(fields=['product', 'is_primary']),
        ]

    def __str__(self):
        return f"{self.product.name} - Image {self.order}"

    def clean(self):
        # Validate image size (max 5MB)
        if self.image:
            if self.image.size > 5 * 1024 * 1024:
                raise ValidationError("Image size cannot exceed 5MB")

    def save(self, *args, **kwargs):
        # Ensure only one primary image per product
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product,
                is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)

        super().save(*args, **kwargs)

        # Optimize image
        if self.image:
            img_path = self.image.path
            img = Image.open(img_path)

            # Convert RGBA to RGB if needed
            if img.mode == 'RGBA':
                img = img.convert('RGB')

            # Resize if too large (max 1920x1920)
            max_size = (1920, 1920)
            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                img.save(img_path, quality=85, optimize=True)


# =========================
# PRODUCT REVIEW MODEL
# =========================
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user']),
            models.Index(fields=['is_verified']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"

    def clean(self):
        # Prevent sellers from reviewing their own products
        if self.product.seller == self.user:
            raise ValidationError("You cannot review your own product")

        # Validate image size if provided
        if self.image and self.image.size > 5 * 1024 * 1024:
            raise ValidationError("Review image size cannot exceed 5MB")

    @property
    def stars(self):
        return '⭐' * self.rating


# =========================
# REVIEW REPLIES (Seller Responses)
# =========================
class ReviewReply(models.Model):
    review = models.ForeignKey(
        ProductReview,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_replies'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['review', 'created_at']),
        ]

    def __str__(self):
        return f"Reply by {self.user.username} on {self.review}"

    def clean(self):
        # Only the product seller can reply to reviews
        if self.review.product.seller != self.user:
            raise ValidationError("Only the product seller can reply to reviews")


# =========================
# HELPFUL VOTES (for Reviews)
# =========================
class ReviewHelpfulVote(models.Model):
    review = models.ForeignKey(
        ProductReview,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='helpful_votes'
    )
    is_helpful = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('review', 'user')
        indexes = [
            models.Index(fields=['review', 'is_helpful']),
        ]

    def __str__(self):
        return f"{self.user.username} marked {self.review} as helpful"


# =========================
# AUDIT LOG MODEL
# =========================
class ProductAuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted (Soft)'),
        ('RESTORE', 'Restored'),
        ('STOCK_CHANGE', 'Stock Changed'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='product_audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    changes = models.JSONField(null=True, blank=True)  # Store what changed
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['product', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.action} - {self.product.name} by {self.user} at {self.timestamp}"


# =========================
# SIGNALS
# =========================
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Product)
def track_stock_changes(sender, instance, **kwargs):
    """Track stock changes for audit log"""
    if instance.pk:
        try:
            old_instance = Product.objects.get(pk=instance.pk)
            if old_instance.stock != instance.stock:
                instance._stock_changed = True
                instance._old_stock = old_instance.stock
        except Product.DoesNotExist:
            pass


@receiver(post_save, sender=Product)
def create_product_audit_log(sender, instance, created, **kwargs):
    """Create audit log for product changes"""
    if created:
        ProductAuditLog.objects.create(
            product=instance,
            user=instance.seller,
            action='CREATE',
            changes={'stock': instance.stock, 'price': str(instance.price)}
        )
    elif hasattr(instance, '_stock_changed') and instance._stock_changed:
        ProductAuditLog.objects.create(
            product=instance,
            user=instance.seller,
            action='STOCK_CHANGE',
            changes={
                'old_stock': instance._old_stock,
                'new_stock': instance.stock
            }
        )

@receiver(post_save, sender=ProductReview)
def mark_verified_review(sender, instance, created, **kwargs):
    if created:
        # Check if user has purchased this product
        from orders.models import Order, OrderItem
        has_purchased = OrderItem.objects.filter(
            order__user=instance.user,
            product=instance.product,
            order__status='completed'
        ).exists()
        
        if has_purchased:
            instance.is_verified = True
            instance.save(update_fields=['is_verified'])