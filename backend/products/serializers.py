from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Category,
    Product,
    ProductImage,
    ProductReview,
    ReviewReply,
    ReviewHelpfulVote,
    ProductAuditLog
)
from django.contrib.auth import get_user_model

User = get_user_model()


# =========================
# CATEGORY SERIALIZER
# =========================
class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'is_active', 'subcategories', 'product_count']
        read_only_fields = ['slug']

    def get_subcategories(self, obj):
        if obj.subcategories.exists():
            return CategorySerializer(obj.subcategories.filter(is_active=True), many=True).data
        return []

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True, is_deleted=False).count()


# =========================
# PRODUCT IMAGE SERIALIZER
# =========================
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']
        read_only_fields = ['id']

    def validate_image(self, value):
        # Validate image size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Image size cannot exceed 5MB")
        
        # Validate image format
        allowed_formats = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError(
                f"Invalid image format. Allowed formats: JPEG, PNG, WebP"
            )
        
        return value


# =========================
# PRODUCT SERIALIZER (List View)
# =========================
class ProductListSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'category_id', 'name', 'slug', 
            'description', 'price', 'stock', 'low_stock_threshold',
            'primary_image', 'is_active', 'is_low_stock', 'is_available',
            'average_rating', 'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'seller']

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


# =========================
# PRODUCT SERIALIZER (Detail View)
# =========================
class ProductDetailSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)
    seller_id = serializers.IntegerField(source='seller.id', read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    is_low_stock = serializers.BooleanField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'seller_id', 'category', 'category_id', 'name', 
            'slug', 'description', 'price', 'stock', 'low_stock_threshold',
            'images', 'is_active', 'is_low_stock', 'is_available',
            'average_rating', 'review_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'seller']

    def get_average_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(avg, 2) if avg else None

    def get_review_count(self, obj):
        return obj.reviews.count()

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value


# =========================
# PRODUCT CREATE/UPDATE SERIALIZER
# =========================
class ProductWriteSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_active=True),
        source='category',
        required=False,
        allow_null=True
    )
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = [
            'id', 'category_id', 'name', 'description', 'price', 
            'stock', 'low_stock_threshold', 'is_active',
            'images', 'uploaded_images'
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

    def validate_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative")
        return value

    def validate_uploaded_images(self, value):
        if len(value) > 10:
            raise serializers.ValidationError("Maximum 10 images allowed per product")
        return value

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)

        # Create product images
        for idx, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                is_primary=(idx == 0),  # First image is primary
                order=idx
            )

        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', None)
        
        # Update product fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle new images if provided
        if uploaded_images:
            current_image_count = instance.images.count()
            for idx, image in enumerate(uploaded_images):
                ProductImage.objects.create(
                    product=instance,
                    image=image,
                    is_primary=(current_image_count == 0 and idx == 0),
                    order=current_image_count + idx
                )

        return instance


# =========================
# REVIEW REPLY SERIALIZER
# =========================
class ReviewReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    is_seller = serializers.SerializerMethodField()

    class Meta:
        model = ReviewReply
        fields = ['id', 'user', 'user_id', 'is_seller', 'content', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_is_seller(self, obj):
        return obj.user == obj.review.product.seller


# =========================
# PRODUCT REVIEW SERIALIZER
# =========================
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)
    helpful_count = serializers.SerializerMethodField()
    user_found_helpful = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'product_name', 'user', 'user_id', 'rating', 
            'title', 'content', 'image', 'is_verified', 'created_at', 
            'updated_at', 'replies', 'helpful_count', 'user_found_helpful'
        ]
        read_only_fields = ['user', 'is_verified', 'created_at', 'updated_at']

    def get_helpful_count(self, obj):
        return obj.helpful_votes.filter(is_helpful=True).count()

    def get_user_found_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.helpful_votes.filter(user=request.user, is_helpful=True).exists()
        return False

    def validate(self, data):
        request = self.context.get('request')
        product = data.get('product')

        # Prevent sellers from reviewing their own products
        if product and product.seller == request.user:
            raise serializers.ValidationError("You cannot review your own product")

        return data

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_image(self, value):
        if value and value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Review image size cannot exceed 5MB")
        return value


# =========================
# HELPFUL VOTE SERIALIZER
# =========================
class ReviewHelpfulVoteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewHelpfulVote
        fields = ['id', 'review', 'user', 'is_helpful', 'created_at']
        read_only_fields = ['user', 'created_at']


# =========================
# AUDIT LOG SERIALIZER
# =========================
class ProductAuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = ProductAuditLog
        fields = ['id', 'user', 'action', 'action_display', 'changes', 'timestamp', 'ip_address']
        read_only_fields = '__all__'


# =========================
# BULK DELETE SERIALIZER
# =========================
class BulkDeleteSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

    def validate_product_ids(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 products can be deleted at once")
        return value