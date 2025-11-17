from django.urls import path
from .views import (
    CartView,
    CartSummaryView,
    AddToCartView,
    UpdateCartItemView,
    RemoveFromCartView,
    ClearCartView,
    ValidateCartView,
    CartAuditLogsView,
)

urlpatterns = [
    # Cart operations
    path('', CartView.as_view(), name='view_cart'),
    path('summary/', CartSummaryView.as_view(), name='cart_summary'),
    path('add/', AddToCartView.as_view(), name='add_to_cart'),
    path('update/', UpdateCartItemView.as_view(), name='update_cart_item'),
    path('remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', ClearCartView.as_view(), name='clear_cart'),
    path('validate/', ValidateCartView.as_view(), name='validate_cart'),
    path('audit-logs/', CartAuditLogsView.as_view(), name='cart_audit_logs'),
]