from rest_framework import serializers
from .models import (
    Category,
    Product,
    ProductReview,
    ReviewReply,
    ReviewHelpfulVote,
)
from django.contrib.auth import get_user_model

User = get_user_model()


# =========================
# CATEGORY SERIALIZER
# =========================
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent']


# =========================
# PRODUCT SERIALIZER
# =========================
class ProductSerializer(serializers.ModelSerializer):
    seller = serializers.StringRelatedField(read_only=True)
    category = CategorySerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'seller', 'category', 'name', 'slug', 'description', 'price',
            'stock', 'image', 'is_active', 'average_rating', 'review_count',
            'created_at', 'updated_at'
        ]


# =========================
# REVIEW REPLY SERIALIZER
# =========================
class ReviewReplySerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewReply
        fields = ['id', 'user', 'content', 'created_at']


# =========================
# PRODUCT REVIEW SERIALIZER
# =========================
class ProductReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = ReviewReplySerializer(many=True, read_only=True)
    helpful_count = serializers.SerializerMethodField()

    class Meta:
        model = ProductReview
        fields = [
            'id', 'user', 'rating', 'title', 'content', 'image',
            'is_verified', 'created_at', 'replies', 'helpful_count'
        ]

    def get_helpful_count(self, obj):
        return obj.helpful_votes.filter(is_helpful=True).count()


# =========================
# HELPFUL VOTE SERIALIZER
# =========================
class ReviewHelpfulVoteSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ReviewHelpfulVote
        fields = ['id', 'user', 'is_helpful', 'created_at']
