from django.db import models
from django.contrib.auth import get_user_model
from autoslug import AutoSlugField
from django.core.validators import MinValueValidator, MaxValueValidator

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

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

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
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


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

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}⭐)"

    @property
    def stars(self):
        return '⭐' * self.rating


# =========================
# REVIEW REPLIES (Seller or User Responses)
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

    def __str__(self):
        return f"Reply by {self.user.username} on {self.review}"


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

    def __str__(self):
        return f"{self.user.username} marked {self.review} as helpful"


# =========================
# OPTIONAL: SIGNALS (auto mark verified review)
# =========================
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=ProductReview)
def mark_verified_review(sender, instance, created, **kwargs):
    """
    Example signal: mark review as verified if the user has an order
    with this product (depends on your Order model).
    You can implement logic later when orders are ready.
    """
    pass
