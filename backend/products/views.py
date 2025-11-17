from rest_framework import serializers
from django.db.models import Avg, Count, Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter, BooleanFilter, CharFilter
from django.utils import timezone
from django.db import transaction
from .models import (
    Category,
    Product,
    ProductImage,
    ProductReview,
    ReviewReply,
    ReviewHelpfulVote,
    ProductAuditLog
)
from .serializers import (
    CategorySerializer,
    ProductListSerializer,
    ProductDetailSerializer,
    ProductWriteSerializer,
    ProductReviewSerializer,
    ReviewReplySerializer,
    ReviewHelpfulVoteSerializer,
    ProductAuditLogSerializer,
    BulkDeleteSerializer,
    ProductImageSerializer
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied, ValidationError


# =========================
# CUSTOM ERROR RESPONSE
# =========================
def error_response(message, status_code=status.HTTP_400_BAD_REQUEST, errors=None):
    """Standardized error response format"""
    response_data = {
        "success": False,
        "message": message,
    }
    if errors:
        response_data["errors"] = errors
    return Response(response_data, status=status_code)


def success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """Standardized success response format"""
    response_data = {
        "success": True,
        "message": message,
    }
    if data is not None:
        response_data["data"] = data
    return Response(response_data, status=status_code)


# =========================
# PERMISSION CLASSES
# =========================
class IsSeller(BasePermission):
    """Custom permission to allow only sellers to manage products."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and hasattr(request.user, 'is_seller') and request.user.is_seller


class IsSellerOrReadOnly(BasePermission):
    """Allow sellers to edit their own products, others can only read"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user


class IsReviewOwnerOrReadOnly(BasePermission):
    """Allow users to edit their own reviews"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsProductSellerForReply(BasePermission):
    """Only product seller can reply to reviews"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        review_id = request.data.get('review')
        if not review_id:
            return False
        
        try:
            review = ProductReview.objects.select_related('product').get(id=review_id)
            return review.product.seller == request.user
        except ProductReview.DoesNotExist:
            return False


# =========================
# PAGINATION CLASSES
# =========================
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReviewPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


# =========================
# PRODUCT FILTERS
# =========================
class ProductFilter(FilterSet):
    min_price = NumberFilter(field_name="price", lookup_expr='gte')
    max_price = NumberFilter(field_name="price", lookup_expr='lte')
    min_rating = NumberFilter(method='filter_min_rating')
    in_stock = BooleanFilter(method='filter_in_stock')
    category = NumberFilter(field_name='category__id')
    search = CharFilter(method='filter_search')

    class Meta:
        model = Product
        fields = ['category', 'is_active']

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_min_rating(self, queryset, name, value):
        return queryset.filter(average_rating__gte=value)

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | 
            Q(description__icontains=value) |
            Q(category__name__icontains=value)
        )


# =========================
# REVIEW FILTERS
# =========================
class ReviewFilter(FilterSet):
    product = NumberFilter(field_name='product__id')
    rating = NumberFilter(field_name='rating')
    verified = BooleanFilter(field_name='is_verified')

    class Meta:
        model = ProductReview
        fields = ['product', 'rating', 'verified']


# =========================
# CATEGORY VIEWSET
# =========================
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True).prefetch_related('subcategories')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None  # No pagination for categories

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(parent__isnull=True)  # Only root categories
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data, message="Categories retrieved successfully")


# =========================
# PRODUCT VIEWSET
# =========================   
class ProductViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsSellerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'average_rating', 'stock']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Product.objects.filter(is_deleted=False).select_related('category', 'seller').prefetch_related('images')
        
        # Annotate with ratings
        queryset = queryset.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

        # If user is not authenticated or not a seller, show only active products
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'is_seller') or not self.request.user.is_seller:
            queryset = queryset.filter(is_active=True)
        # If seller is viewing their own products (my-products action)
        elif self.action == 'my_products':
            queryset = queryset.filter(seller=self.request.user)
        # Otherwise show all active products (sellers browsing marketplace)
        else:
            queryset = queryset.filter(is_active=True)

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        return ProductListSerializer

    def create(self, request, *args, **kwargs):
        # Check if user is a seller
        if not hasattr(request.user, 'is_seller') or not request.user.is_seller:
            return error_response("You must be a seller to create products", status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            product = serializer.save(seller=request.user)
            
            # Create audit log
            ProductAuditLog.objects.create(
                product=product,
                user=request.user,
                action='CREATE',
                changes={'stock': product.stock, 'price': str(product.price)},
                ip_address=self.get_client_ip(request)
            )

        return success_response(
            ProductDetailSerializer(product, context={'request': request}).data,
            message="Product created successfully",
            status_code=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check permission
        if instance.seller != request.user:
            return error_response("You can only update your own products", status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Track changes
            old_data = {
                'price': str(instance.price),
                'stock': instance.stock,
                'is_active': instance.is_active
            }
            
            product = serializer.save()
            
            # Create audit log
            new_data = {
                'price': str(product.price),
                'stock': product.stock,
                'is_active': product.is_active
            }
            
            changes = {k: {'old': old_data[k], 'new': new_data[k]} 
                      for k in old_data if old_data[k] != new_data[k]}
            
            if changes:
                ProductAuditLog.objects.create(
                    product=product,
                    user=request.user,
                    action='UPDATE',
                    changes=changes,
                    ip_address=self.get_client_ip(request)
                )

        return success_response(
            ProductDetailSerializer(product, context={'request': request}).data,
            message="Product updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check permission
        if instance.seller != request.user:
            return error_response("You can only delete your own products", status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            # Soft delete
            instance.is_deleted = True
            instance.deleted_at = timezone.now()
            instance.is_active = False
            instance.save()
            
            # Create audit log
            ProductAuditLog.objects.create(
                product=instance,
                user=request.user,
                action='DELETE',
                ip_address=self.get_client_ip(request)
            )

        return success_response(message="Product deleted successfully", status_code=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_products(self, request):
        """Get products owned by the current seller"""
        if not hasattr(request.user, 'is_seller') or not request.user.is_seller:
            return error_response("Only sellers can access this endpoint", status.HTTP_403_FORBIDDEN)

        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)

        serializer = ProductListSerializer(queryset, many=True, context={'request': request})
        return success_response(serializer.data, message="Your products retrieved successfully")

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bulk_delete(self, request):
        """Bulk soft delete products"""
        if not hasattr(request.user, 'is_seller') or not request.user.is_seller:
            return error_response("Only sellers can delete products", status.HTTP_403_FORBIDDEN)

        serializer = BulkDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_ids = serializer.validated_data['product_ids']
        
        with transaction.atomic():
            products = Product.objects.filter(
                id__in=product_ids,
                seller=request.user,
                is_deleted=False
            )
            
            count = products.count()
            
            if count == 0:
                return error_response("No products found to delete", status.HTTP_404_NOT_FOUND)

            # Soft delete all
            products.update(
                is_deleted=True,
                deleted_at=timezone.now(),
                is_active=False
            )
            
            # Create audit logs
            for product in products:
                ProductAuditLog.objects.create(
                    product=product,
                    user=request.user,
                    action='DELETE',
                    ip_address=self.get_client_ip(request)
                )

        return success_response(
            {'deleted_count': count},
            message=f"{count} product(s) deleted successfully"
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_images(self, request, pk=None):
        """Add images to existing product"""
        product = self.get_object()
        
        if product.seller != request.user:
            return error_response("You can only add images to your own products", status.HTTP_403_FORBIDDEN)

        images = request.FILES.getlist('images')
        
        if not images:
            return error_response("No images provided")

        if len(images) > 10:
            return error_response("Maximum 10 images can be uploaded at once")

        current_count = product.images.count()
        if current_count + len(images) > 10:
            return error_response(f"Product can have maximum 10 images. Currently has {current_count}")

        with transaction.atomic():
            created_images = []
            for idx, image in enumerate(images):
                product_image = ProductImage.objects.create(
                    product=product,
                    image=image,
                    is_primary=(current_count == 0 and idx == 0),
                    order=current_count + idx
                )
                created_images.append(product_image)

        serializer = ProductImageSerializer(created_images, many=True, context={'request': request})
        return success_response(serializer.data, message="Images added successfully", status_code=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        """Delete a product image"""
        product = self.get_object()
        
        if product.seller != request.user:
            return error_response("You can only delete images from your own products", status.HTTP_403_FORBIDDEN)

        image_id = request.data.get('image_id')
        if not image_id:
            return error_response("image_id is required")

        try:
            image = ProductImage.objects.get(id=image_id, product=product)
            image.delete()
            return success_response(message="Image deleted successfully")
        except ProductImage.DoesNotExist:
            return error_response("Image not found", status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        """Get audit logs for a product"""
        product = self.get_object()
        
        # Only seller can view audit logs
        if product.seller != request.user:
            return error_response("You can only view audit logs for your own products", status.HTTP_403_FORBIDDEN)

        logs = ProductAuditLog.objects.filter(product=product).select_related('user')
        serializer = ProductAuditLogSerializer(logs, many=True)
        return success_response(serializer.data, message="Audit logs retrieved successfully")

    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# =========================
# PRODUCT REVIEW VIEWSET
# =========================
class ProductReviewViewSet(viewsets.ModelViewSet):
    queryset = ProductReview.objects.all().select_related('product', 'user').prefetch_related('replies', 'helpful_votes')
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsReviewOwnerOrReadOnly]
    pagination_class = ReviewPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating', 'helpful_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add helpful_count annotation for sorting
        queryset = queryset.annotate(
            helpful_count=Count('helpful_votes', filter=Q(helpful_votes__is_helpful=True))
        )
        
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                review = serializer.save(user=request.user)
                
            return success_response(
                ProductReviewSerializer(review, context={'request': request}).data,
                message="Review created successfully",
                status_code=status.HTTP_201_CREATED
            )
        except Exception as e:
            return error_response(str(e), status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        partial = kwargs.pop('partial', False)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        
        return success_response(
            ProductReviewSerializer(review, context={'request': request}).data,
            message="Review updated successfully"
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return success_response(message="Review deleted successfully", status_code=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def vote_helpful(self, request, pk=None):
        """Mark review as helpful"""
        review = self.get_object()
        
        with transaction.atomic():
            vote, created = ReviewHelpfulVote.objects.get_or_create(
                review=review,
                user=request.user,
                defaults={'is_helpful': True}
            )
            
            if not created:
                # Toggle vote
                vote.is_helpful = not vote.is_helpful
                vote.save()

        message = "Marked as helpful" if vote.is_helpful else "Unmarked as helpful"
        return success_response({'is_helpful': vote.is_helpful}, message=message)


# =========================
# REVIEW REPLY VIEWSET
# =========================
class ReviewReplyViewSet(viewsets.ModelViewSet):
    queryset = ReviewReply.objects.all().select_related('review', 'user', 'review__product')
    serializer_class = ReviewReplySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = ReviewPagination

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsProductSellerForReply()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                reply = serializer.save(user=request.user)
                
            return success_response(
                ReviewReplySerializer(reply, context={'request': request}).data,
                message="Reply created successfully",
                status_code=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return error_response(str(e), status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = super().get_queryset()
        review_id = self.request.query_params.get('review')
        if review_id:
            queryset = queryset.filter(review_id=review_id)
        return queryset


# =========================
# HELPFUL VOTE VIEWSET
# =========================
class ReviewHelpfulVoteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReviewHelpfulVote.objects.all().select_related('review', 'user')
    serializer_class = ReviewHelpfulVoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReviewPagination