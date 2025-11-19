from django.urls import path
from .views import (
    # Profile
    ProfileDetailView, ProfileAvatarUploadView,
    
    # Addresses
    AddressListCreateView, AddressDetailView, SetDefaultAddressView,
    
    # Notification Preferences
    NotificationPreferenceView,
    
    # Seller Profile
    SellerProfileDetailView, SellerStoreLogoUploadView,
    SellerStoreBannerUploadView, PublicSellerProfileView,
    
    # Dashboard
    UserDashboardView, DashboardStatsView,
    BuyerDashboardView, SellerDashboardView,
)

urlpatterns = [
    # Profile endpoints
    path('profile/', ProfileDetailView.as_view(), name='profile_detail'),
    path('profile/avatar/', ProfileAvatarUploadView.as_view(), name='profile_avatar_upload'),
    
    # Address endpoints
    path('addresses/', AddressListCreateView.as_view(), name='address_list_create'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
    path('addresses/<int:pk>/set-default/', SetDefaultAddressView.as_view(), name='set_default_address'),
    
    # Notification preferences
    path('notifications/preferences/', NotificationPreferenceView.as_view(), name='notification_preferences'),
    
    # Seller profile endpoints
    path('seller/profile/', SellerProfileDetailView.as_view(), name='seller_profile_detail'),
    path('seller/profile/logo/', SellerStoreLogoUploadView.as_view(), name='seller_logo_upload'),
    path('seller/profile/banner/', SellerStoreBannerUploadView.as_view(), name='seller_banner_upload'),
    path('seller/<slug:store_slug>/', PublicSellerProfileView.as_view(), name='public_seller_profile'),
    
    # Dashboard endpoints
    path('dashboard/', UserDashboardView.as_view(), name='user_dashboard'),
    path('dashboard/stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('dashboard/buyer/', BuyerDashboardView.as_view(), name='buyer_dashboard'),
    path('dashboard/seller/', SellerDashboardView.as_view(), name='seller_dashboard'),
]