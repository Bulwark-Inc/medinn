from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Profile, Address, NotificationPreference, SellerProfile
from .serializers import (
    ProfileSerializer, AddressSerializer, NotificationPreferenceSerializer,
    SellerProfileSerializer, UserProfileSerializer, DashboardStatsSerializer
)
from .permissions import IsOwner, IsSeller, IsSellerOwner
from .utils import (
    resize_avatar, resize_store_logo, resize_store_banner,
    validate_image_file, log_profile_event, get_dashboard_stats
)


# ========== Profile Views ==========

class ProfileDetailView(APIView):
    """Get or update user profile"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            
            # Log the event
            log_profile_event(request.user, 'profile_updated', details={'fields': list(request.data.keys())})
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class ProfileAvatarUploadView(APIView):
    """Upload or update profile avatar"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        profile = request.user.profile
        avatar = request.FILES.get('avatar')

        if not avatar:
            return Response({'detail': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate image
        is_valid, error_message = validate_image_file(avatar)
        if not is_valid:
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        # Resize and save avatar
        try:
            resized_avatar = resize_avatar(avatar)
            
            # Delete old avatar if exists
            if profile.avatar:
                profile.avatar.delete(save=False)
            
            profile.avatar = resized_avatar
            profile.save()

            # Log the event
            log_profile_event(request.user, 'avatar_changed')

            serializer = ProfileSerializer(profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Error processing image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        """Delete profile avatar"""
        profile = request.user.profile
        
        if profile.avatar:
            profile.avatar.delete(save=True)
            log_profile_event(request.user, 'avatar_changed', details={'action': 'deleted'})
            return Response({'message': 'Avatar deleted successfully.'}, status=status.HTTP_200_OK)
        
        return Response({'detail': 'No avatar to delete.'}, status=status.HTTP_400_BAD_REQUEST)


# =====x===== Profile Views =====x=====


# ========== Address Views ==========

class AddressListCreateView(generics.ListCreateAPIView):
    """List all addresses or create a new address"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        log_profile_event(self.request.user, 'address_added', details={'address_id': serializer.instance.id})


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete an address"""
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        log_profile_event(self.request.user, 'address_updated', details={'address_id': serializer.instance.id})

    def perform_destroy(self, instance):
        address_id = instance.id
        instance.delete()
        log_profile_event(self.request.user, 'address_deleted', details={'address_id': address_id})


class SetDefaultAddressView(APIView):
    """Set an address as default"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user=request.user)
            
            # Unset other defaults of same type
            Address.objects.filter(
                user=request.user,
                address_type=address.address_type,
                is_default=True
            ).exclude(pk=pk).update(is_default=False)
            
            # Set this as default
            address.is_default = True
            address.save()
            
            serializer = AddressSerializer(address)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Address.DoesNotExist:
            return Response({'detail': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)


# =====x===== Address Views =====x=====


# ========== Notification Preferences Views ==========

class NotificationPreferenceView(APIView):
    """Get or update notification preferences"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences = request.user.notification_preferences
        serializer = NotificationPreferenceSerializer(preferences)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        preferences = request.user.notification_preferences
        serializer = NotificationPreferenceSerializer(
            preferences, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


# =====x===== Notification Preferences Views =====x=====


# ========== Seller Profile Views ==========

class SellerProfileDetailView(APIView):
    """Get or update seller profile"""
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request):
        seller_profile = request.user.seller_profile
        serializer = SellerProfileSerializer(seller_profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        seller_profile = request.user.seller_profile
        serializer = SellerProfileSerializer(
            seller_profile, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            log_profile_event(request.user, 'seller_profile_updated', details={'fields': list(request.data.keys())})
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        return self.put(request)


class SellerStoreLogoUploadView(APIView):
    """Upload or update store logo"""
    permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        seller_profile = request.user.seller_profile
        logo = request.FILES.get('logo')

        if not logo:
            return Response({'detail': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate image
        is_valid, error_message = validate_image_file(logo)
        if not is_valid:
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resized_logo = resize_store_logo(logo)
            
            if seller_profile.store_logo:
                seller_profile.store_logo.delete(save=False)
            
            seller_profile.store_logo = resized_logo
            seller_profile.save()

            serializer = SellerProfileSerializer(seller_profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Error processing image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SellerStoreBannerUploadView(APIView):
    """Upload or update store banner"""
    permission_classes = [IsAuthenticated, IsSeller]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        seller_profile = request.user.seller_profile
        banner = request.FILES.get('banner')

        if not banner:
            return Response({'detail': 'No image file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate image
        is_valid, error_message = validate_image_file(banner)
        if not is_valid:
            return Response({'detail': error_message}, status=status.HTTP_400_BAD_REQUEST)

        try:
            resized_banner = resize_store_banner(banner)
            
            if seller_profile.store_banner:
                seller_profile.store_banner.delete(save=False)
            
            seller_profile.store_banner = resized_banner
            seller_profile.save()

            serializer = SellerProfileSerializer(seller_profile, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Error processing image: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicSellerProfileView(APIView):
    """Public view of seller profile (by store slug)"""
    permission_classes = []

    def get(self, request, store_slug):
        seller_profile = get_object_or_404(SellerProfile, store_slug=store_slug, is_active=True)
        serializer = SellerProfileSerializer(seller_profile, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


# =====x===== Seller Profile Views =====x=====


# ========== Dashboard Views ==========

class UserDashboardView(APIView):
    """Complete user profile with all related data"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardStatsView(APIView):
    """Get dashboard statistics"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = get_dashboard_stats(request.user)
        serializer = DashboardStatsSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BuyerDashboardView(APIView):
    """Buyer-specific dashboard"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Get stats
        stats = get_dashboard_stats(user)
        
        # Get profile data
        profile_serializer = ProfileSerializer(user.profile, context={'request': request})
        
        # Get addresses
        addresses = Address.objects.filter(user=user)
        address_serializer = AddressSerializer(addresses, many=True)
        
        # Get recent orders (will populate when orders app is ready)
        recent_orders = []
        if hasattr(user, 'orders'):
            from orders.serializers import OrderSerializer  # Import when ready
            recent_orders_qs = user.orders.all().order_by('-created_at')[:5]
            # recent_orders = OrderSerializer(recent_orders_qs, many=True).data
        
        return Response({
            'stats': stats,
            'profile': profile_serializer.data,
            'addresses': address_serializer.data,
            'recent_orders': recent_orders,
        }, status=status.HTTP_200_OK)


class SellerDashboardView(APIView):
    """Seller-specific dashboard"""
    permission_classes = [IsAuthenticated, IsSeller]

    def get(self, request):
        user = request.user
        
        # Get stats
        stats = get_dashboard_stats(user)
        
        # Get seller profile
        seller_profile_serializer = SellerProfileSerializer(user.seller_profile, context={'request': request})
        
        # Get recent products (will populate when products are available)
        recent_products = []
        if hasattr(user, 'products'):
            from products.serializers import ProductSerializer  # Already exists
            recent_products_qs = user.products.all().order_by('-created_at')[:5]
            # recent_products = ProductSerializer(recent_products_qs, many=True, context={'request': request}).data
        
        # Get recent orders (seller orders)
        recent_orders = []
        if hasattr(user, 'seller_orders'):
            from orders.serializers import OrderSerializer  # Import when ready
            recent_orders_qs = user.seller_orders.all().order_by('-created_at')[:5]
            # recent_orders = OrderSerializer(recent_orders_qs, many=True).data
        
        return Response({
            'stats': stats,
            'seller_profile': seller_profile_serializer.data,
            'recent_products': recent_products,
            'recent_orders': recent_orders,
        }, status=status.HTTP_200_OK)


# =====x===== Dashboard Views =====x=====