from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductReviewViewSet,
    ReviewReplyViewSet,
    ReviewHelpfulVoteViewSet,
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'replies', ReviewReplyViewSet, basename='reply')
router.register(r'votes', ReviewHelpfulVoteViewSet, basename='vote')

urlpatterns = [
    path('', include(router.urls)),
]
