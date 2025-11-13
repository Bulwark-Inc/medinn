from django.db.models import Avg, Count, Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, BooleanFilter
from .models import (
    Category,
    Product,
    ProductReview,
    ReviewReply,
    ReviewHelpfulVote
)
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductReviewSerializer,
    ReviewReplySerializer,
    ReviewHelpfulVoteSerializer
)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied


# =========================
# PERMISSION CLASS
# =========================
class IsSeller(BasePermission):
    """
    Custom permission to allow only sellers to manage products.
    """
    def has_permission(self, request, view):
        # If the request method is a safe method (GET, HEAD, OPTIONS), allow all users
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        # For other methods (POST, PUT, DELETE), check if the user is a seller
        return request.user.is_authenticated and request.user.is_seller


# =========================
# PAGINATION CLASS
# =========================
class DefaultPagination(LimitOffsetPagination):
    default_limit = 12
    max_limit = 50


# =========================
# PRODUCT FILTERS
# =========================
class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name="price", lookup_expr='gte')
    max_price = NumberFilter(field_name="price", lookup_expr='lte')
    min_rating = NumberFilter(method='filter_min_rating')
    in_stock = BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'seller', 'is_active']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_min_rating(self, queryset, name, value):
        # Ensure average_rating is annotated before filtering
        queryset = queryset.annotate(average_rating=Avg('reviews__rating'))
        return queryset.filter(average_rating__gte=value)


# =========================
# CATEGORY VIEWSET
# =========================
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


# =========================
# PRODUCT VIEWSET
# =========================   
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    pagination_class = DefaultPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]  # Read-only for non-authenticated users

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'updated_at', 'average_rating']
    ordering = ['-created_at']

    def get_queryset(self):
        # If the user is a seller, only show their products
        if self.request.user.is_authenticated and self.request.user.is_seller:
            return Product.objects.filter(seller=self.request.user, is_active=True)  # Seller can only manage their own products

        # Regular users can view all active products
        return (
            Product.objects.filter(is_active=True)
            .annotate(
                average_rating=Avg('reviews__rating'),
                review_count=Count('reviews')
            )
            .select_related('category', 'seller')
        )

    def perform_create(self, serializer):
        # Only sellers can create products and they should be associated with the seller
        if self.request.user.is_seller:
            serializer.save(seller=self.request.user)
        else:
            raise PermissionDenied("You must be a seller to add products.")

    def perform_update(self, serializer):
        # Ensure the product being updated belongs to the seller
        product = self.get_object()
        if product.seller == self.request.user or self.request.user.is_staff:
            serializer.save()
        else:
            raise PermissionDenied("You can only update your own products.")

    def perform_destroy(self, instance):
        # Ensure the product being deleted belongs to the seller
        if instance.seller == self.request.user or self.request.user.is_staff:
            instance.delete()
        else:
            raise PermissionDenied("You can only delete your own products.")


# =========================
# PRODUCT REVIEW VIEWSET
# =========================
class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all().select_related('product', 'user')
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        product_id = self.request.query_params.get('product')
        qs = self.queryset
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote_helpful(self, request, pk=None):
        review = self.get_object()
        vote, created = ReviewHelpfulVote.objects.get_or_create(
            review=review, user=request.user
        )
        vote.is_helpful = True
        vote.save()
        return Response({"message": "Marked as helpful"}, status=status.HTTP_200_OK)


# =========================
# REVIEW REPLY VIEWSET
# =========================
class ReviewReplyViewSet(viewsets.ModelViewSet):
    queryset = ReviewReply.objects.all().select_related('review', 'user')
    serializer_class = ReviewReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# =========================
# HELPFUL VOTE VIEWSET (optional direct access)
# =========================
class ReviewHelpfulVoteViewSet(viewsets.ModelViewSet):
    queryset = ReviewHelpfulVote.objects.all().select_related('review', 'user')
    serializer_class = ReviewHelpfulVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
