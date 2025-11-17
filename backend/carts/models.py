from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from products.models import Product
from decimal import Decimal


# =========================
# CART MODEL
# =========================
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Cart for {self.user.username}"

    @property
    def total_items(self):
        """Get total number of items in cart"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def subtotal(self):
        """Calculate cart subtotal (sum of all item totals)"""
        total = Decimal('0.00')
        for item in self.items.all():
            total += item.total_price
        return total

    @property
    def has_unavailable_items(self):
        """Check if cart has any unavailable items"""
        return self.items.filter(
            models.Q(product__is_active=False) |
            models.Q(product__is_deleted=True) |
            models.Q(product__stock=0)
        ).exists()

    @property
    def has_stock_issues(self):
        """Check if any item quantity exceeds available stock"""
        for item in self.items.select_related('product'):
            if item.quantity > item.product.stock:
                return True
        return False

    def clear(self):
        """Remove all items from cart"""
        self.items.all().delete()


# =========================
# CART ITEM MODEL
# =========================
class CartItem(models.Model):
    MAX_QUANTITY_PER_ITEM = 99  # Maximum quantity allowed per cart item

    cart = models.ForeignKey(
        Cart,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(MAX_QUANTITY_PER_ITEM)
        ]
    )
    # Price snapshot - store price at time of adding to cart
    price_at_addition = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price of product when added to cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('cart', 'product')
        indexes = [
            models.Index(fields=['cart', 'product']),
            models.Index(fields=['product']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"

    def clean(self):
        """Validate cart item"""
        # Check if product is available
        if not self.product.is_available:
            raise ValidationError("This product is not available for purchase")

        # Check if seller is trying to add their own product
        if self.cart.user == self.product.seller:
            raise ValidationError("You cannot add your own products to cart")

        # Check stock availability
        if self.quantity > self.product.stock:
            raise ValidationError(
                f"Only {self.product.stock} unit(s) available for {self.product.name}"
            )

        # Check max quantity limit
        if self.quantity > self.MAX_QUANTITY_PER_ITEM:
            raise ValidationError(
                f"Maximum {self.MAX_QUANTITY_PER_ITEM} units allowed per item"
            )

    def save(self, *args, **kwargs):
        # Set price snapshot on creation
        if not self.pk:
            self.price_at_addition = self.product.price
        
        # Run validation
        self.clean()
        super().save(*args, **kwargs)

    @property
    def total_price(self):
        """Calculate total price for this cart item using snapshot price"""
        return self.price_at_addition * self.quantity

    @property
    def current_price(self):
        """Get current product price"""
        return self.product.price

    @property
    def price_changed(self):
        """Check if product price has changed since adding to cart"""
        return self.price_at_addition != self.product.price

    @property
    def price_difference(self):
        """Calculate price difference (positive if price increased, negative if decreased)"""
        return self.product.price - self.price_at_addition

    @property
    def is_available(self):
        """Check if product is still available"""
        return self.product.is_available

    @property
    def has_sufficient_stock(self):
        """Check if product has sufficient stock for requested quantity"""
        return self.product.stock >= self.quantity

    @property
    def stock_status(self):
        """Get stock status message"""
        if not self.is_available:
            return "unavailable"
        elif not self.has_sufficient_stock:
            return "insufficient_stock"
        elif self.product.is_low_stock:
            return "low_stock"
        return "in_stock"


# =========================
# CART AUDIT LOG MODEL
# =========================
class CartAuditLog(models.Model):
    ACTION_CHOICES = [
        ('ADD', 'Item Added'),
        ('UPDATE', 'Item Updated'),
        ('REMOVE', 'Item Removed'),
        ('CLEAR', 'Cart Cleared'),
    ]

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cart_audit_logs'
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    changes = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['cart', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.action} - {self.cart} at {self.timestamp}"


# =========================
# SIGNALS
# =========================
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver

@receiver(post_save, sender=CartItem)
def log_cart_item_changes(sender, instance, created, **kwargs):
    """Log cart item additions and updates"""
    if created:
        CartAuditLog.objects.create(
            cart=instance.cart,
            user=instance.cart.user,
            action='ADD',
            product=instance.product,
            changes={
                'quantity': instance.quantity,
                'price': str(instance.price_at_addition)
            }
        )
    else:
        # Check if quantity changed
        if hasattr(instance, '_old_quantity'):
            CartAuditLog.objects.create(
                cart=instance.cart,
                user=instance.cart.user,
                action='UPDATE',
                product=instance.product,
                changes={
                    'old_quantity': instance._old_quantity,
                    'new_quantity': instance.quantity
                }
            )


@receiver(pre_save, sender=CartItem)
def track_quantity_changes(sender, instance, **kwargs):
    """Track quantity changes before save"""
    if instance.pk:
        try:
            old_instance = CartItem.objects.get(pk=instance.pk)
            if old_instance.quantity != instance.quantity:
                instance._old_quantity = old_instance.quantity
        except CartItem.DoesNotExist:
            pass


@receiver(post_delete, sender=CartItem)
def log_cart_item_deletion(sender, instance, **kwargs):
    """Log cart item removal"""
    CartAuditLog.objects.create(
        cart=instance.cart,
        user=instance.cart.user,
        action='REMOVE',
        product=instance.product,
        changes={
            'quantity': instance.quantity,
            'price': str(instance.price_at_addition)
        }
    )