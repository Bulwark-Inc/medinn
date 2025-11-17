from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Cart, CartItem, CartAuditLog
from products.models import Product
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
    RemoveFromCartSerializer,
    CartAuditLogSerializer,
    CartSummarySerializer
)


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
# HELPER FUNCTION
# =========================
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# =========================
# CART VIEW
# =========================
class CartView(APIView):
    """
    GET: Retrieve user's cart with all items and details
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.prefetch_related(
            'items__product__images',
            'items__product__seller'
        ).get_or_create(user=request.user)
        
        serializer = CartSerializer(cart, context={'request': request})
        
        # Add warnings if there are issues
        warnings = []
        if cart.has_unavailable_items:
            warnings.append("Some items in your cart are no longer available")
        if cart.has_stock_issues:
            warnings.append("Some items have insufficient stock")
        
        response_data = serializer.data
        if warnings:
            response_data['warnings'] = warnings
        
        return success_response(
            response_data,
            message="Cart retrieved successfully"
        )


# =========================
# CART SUMMARY VIEW
# =========================
class CartSummaryView(APIView):
    """
    GET: Get lightweight cart summary (total items and subtotal)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSummarySerializer(cart)
        return success_response(
            serializer.data,
            message="Cart summary retrieved successfully"
        )


# =========================
# ADD TO CART VIEW
# =========================
class AddToCartView(APIView):
    """
    POST: Add item to cart or update quantity if already exists
    Body: {product_id: int, quantity: int (default: 1)}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            with transaction.atomic():
                # Get or create cart
                cart, _ = Cart.objects.get_or_create(user=request.user)
                
                # Get product
                product = Product.objects.select_for_update().get(
                    id=product_id,
                    is_active=True,
                    is_deleted=False
                )

                # Check if item already exists in cart
                cart_item, created = CartItem.objects.select_for_update().get_or_create(
                    cart=cart,
                    product=product,
                    defaults={
                        'quantity': quantity,
                        'price_at_addition': product.price
                    }
                )

                if not created:
                    # Update existing item
                    new_quantity = cart_item.quantity + quantity
                    
                    # Check against max limit
                    if new_quantity > CartItem.MAX_QUANTITY_PER_ITEM:
                        return error_response(
                            f"Cannot add more. Maximum {CartItem.MAX_QUANTITY_PER_ITEM} units allowed per item"
                        )
                    
                    # Check stock
                    if new_quantity > product.stock:
                        return error_response(
                            f"Cannot add more. Only {product.stock} unit(s) available"
                        )
                    
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    message = "Cart item quantity updated"
                else:
                    message = "Item added to cart successfully"

                # Return updated cart item
                item_serializer = CartItemSerializer(
                    cart_item,
                    context={'request': request}
                )
                
                return success_response(
                    item_serializer.data,
                    message=message,
                    status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )

        except Product.DoesNotExist:
            return error_response(
                "Product not found or unavailable",
                status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(
                f"An error occurred: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================
# UPDATE CART ITEM VIEW
# =========================
class UpdateCartItemView(APIView):
    """
    PATCH: Update cart item quantity
    Body: {product_id: int, quantity: int}
    Note: quantity=0 will just set quantity to 0 (not delete)
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = UpdateCartItemSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            with transaction.atomic():
                cart = Cart.objects.get(user=request.user)
                
                cart_item = CartItem.objects.select_for_update().get(
                    cart=cart,
                    product_id=product_id
                )

                # Update quantity (including 0)
                cart_item.quantity = quantity
                cart_item.save()

                # Log the update
                CartAuditLog.objects.create(
                    cart=cart,
                    user=request.user,
                    action='UPDATE',
                    product=cart_item.product,
                    changes={'quantity': quantity},
                    ip_address=get_client_ip(request)
                )

                item_serializer = CartItemSerializer(
                    cart_item,
                    context={'request': request}
                )
                
                return success_response(
                    item_serializer.data,
                    message="Cart item updated successfully"
                )

        except Cart.DoesNotExist:
            return error_response(
                "Cart not found",
                status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return error_response(
                "Item not found in cart",
                status.HTTP_404_NOT_FOUND
            )
        except ValidationError as e:
            return error_response(str(e), status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return error_response(
                f"An error occurred: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================
# REMOVE FROM CART VIEW
# =========================
class RemoveFromCartView(APIView):
    """
    DELETE: Remove item from cart
    Body: {product_id: int}
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        serializer = RemoveFromCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return error_response(
                "Validation failed",
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )

        product_id = serializer.validated_data['product_id']

        try:
            with transaction.atomic():
                cart = Cart.objects.get(user=request.user)
                
                cart_item = CartItem.objects.get(
                    cart=cart,
                    product_id=product_id
                )
                
                cart_item.delete()

                return success_response(
                    message="Item removed from cart successfully",
                    status_code=status.HTTP_200_OK
                )

        except Cart.DoesNotExist:
            return error_response(
                "Cart not found",
                status.HTTP_404_NOT_FOUND
            )
        except CartItem.DoesNotExist:
            return error_response(
                "Item not found in cart",
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                f"An error occurred: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================
# CLEAR CART VIEW
# =========================
class ClearCartView(APIView):
    """
    DELETE: Remove all items from cart
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            with transaction.atomic():
                cart = Cart.objects.get(user=request.user)
                
                # Get count before clearing
                item_count = cart.items.count()
                
                if item_count == 0:
                    return error_response(
                        "Cart is already empty",
                        status.HTTP_400_BAD_REQUEST
                    )
                
                # Clear cart
                cart.clear()
                
                # Log the action
                CartAuditLog.objects.create(
                    cart=cart,
                    user=request.user,
                    action='CLEAR',
                    changes={'items_removed': item_count},
                    ip_address=get_client_ip(request)
                )

                return success_response(
                    {'items_removed': item_count},
                    message="Cart cleared successfully"
                )

        except Cart.DoesNotExist:
            return error_response(
                "Cart not found",
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                f"An error occurred: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================
# VALIDATE CART VIEW
# =========================
class ValidateCartView(APIView):
    """
    GET: Validate cart items (check availability, stock, price changes)
    Returns list of issues if any
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.prefetch_related(
                'items__product'
            ).get(user=request.user)
            
            issues = []
            
            for item in cart.items.all():
                item_issues = []
                
                # Check availability
                if not item.is_available:
                    item_issues.append("Product is no longer available")
                
                # Check stock
                if not item.has_sufficient_stock:
                    item_issues.append(
                        f"Insufficient stock. Only {item.product.stock} available"
                    )
                
                # Check price changes
                if item.price_changed:
                    diff = item.price_difference
                    if diff > 0:
                        item_issues.append(
                            f"Price increased by {abs(diff)}"
                        )
                    else:
                        item_issues.append(
                            f"Price decreased by {abs(diff)}"
                        )
                
                if item_issues:
                    issues.append({
                        'product_id': item.product.id,
                        'product_name': item.product.name,
                        'issues': item_issues
                    })
            
            if issues:
                return success_response(
                    {
                        'valid': False,
                        'issues': issues
                    },
                    message="Cart has validation issues"
                )
            else:
                return success_response(
                    {'valid': True},
                    message="Cart is valid"
                )

        except Cart.DoesNotExist:
            return error_response(
                "Cart not found",
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                f"An error occurred: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================
# CART AUDIT LOGS VIEW
# =========================
class CartAuditLogsView(APIView):
    """
    GET: Get audit logs for user's cart
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            logs = CartAuditLog.objects.filter(cart=cart).select_related(
                'user', 'product'
            )[:50]  # Last 50 logs
            
            serializer = CartAuditLogSerializer(logs, many=True)
            return success_response(
                serializer.data,
                message="Audit logs retrieved successfully"
            )

        except Cart.DoesNotExist:
            return error_response(
                "Cart not found",
                status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return error_response(
                f"An error occurred: {str(e)}",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )