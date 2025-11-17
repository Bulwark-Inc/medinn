from rest_framework import serializers
from .models import Cart, CartItem, CartAuditLog
from products.models import Product
from products.serializers import ProductImageSerializer


# =========================
# PRODUCT MINI SERIALIZER (for cart items)
# =========================
class ProductMiniSerializer(serializers.ModelSerializer):
    """Lightweight product serializer for cart display"""
    primary_image = serializers.SerializerMethodField()
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'price', 'stock', 
            'primary_image', 'seller_name', 'is_available', 'is_low_stock'
        ]
        read_only_fields = fields

    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None


# =========================
# CART ITEM SERIALIZER
# =========================
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductMiniSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True, is_deleted=False),
        source='product',
        write_only=True
    )
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    current_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    price_changed = serializers.BooleanField(read_only=True)
    price_difference = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    is_available = serializers.BooleanField(read_only=True)
    has_sufficient_stock = serializers.BooleanField(read_only=True)
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 
            'price_at_addition', 'current_price', 'total_price',
            'price_changed', 'price_difference', 'is_available',
            'has_sufficient_stock', 'stock_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'price_at_addition', 'created_at', 'updated_at']

    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        
        if value > CartItem.MAX_QUANTITY_PER_ITEM:
            raise serializers.ValidationError(
                f"Maximum {CartItem.MAX_QUANTITY_PER_ITEM} units allowed per item"
            )
        
        return value

    def validate_product_id(self, product):
        """Validate product before adding to cart"""
        request = self.context.get('request')
        
        # Check if product is available
        if not product.is_available:
            raise serializers.ValidationError("This product is not available for purchase")
        
        # Check if seller is trying to add their own product
        if request and request.user == product.seller:
            raise serializers.ValidationError("You cannot add your own products to cart")
        
        return product

    def validate(self, data):
        """Cross-field validation"""
        product = data.get('product')
        quantity = data.get('quantity', 1)
        
        # Check stock availability
        if product and quantity > product.stock:
            raise serializers.ValidationError({
                'quantity': f"Only {product.stock} unit(s) available for {product.name}"
            })
        
        return data


# =========================
# CART SERIALIZER
# =========================
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    has_unavailable_items = serializers.BooleanField(read_only=True)
    has_stock_issues = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'items', 'total_items', 'subtotal',
            'has_unavailable_items', 'has_stock_issues',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


# =========================
# ADD TO CART SERIALIZER
# =========================
class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_quantity(self, value):
        if value > CartItem.MAX_QUANTITY_PER_ITEM:
            raise serializers.ValidationError(
                f"Maximum {CartItem.MAX_QUANTITY_PER_ITEM} units allowed per item"
            )
        return value

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value, is_active=True, is_deleted=False)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or unavailable")
        
        # Check if product is available
        if not product.is_available:
            raise serializers.ValidationError("This product is not available for purchase")
        
        return value

    def validate(self, data):
        """Cross-field validation"""
        try:
            product = Product.objects.get(id=data['product_id'])
            quantity = data['quantity']
            
            # Check stock
            if quantity > product.stock:
                raise serializers.ValidationError({
                    'quantity': f"Only {product.stock} unit(s) available"
                })
            
            # Check if seller is trying to add their own product
            request = self.context.get('request')
            if request and request.user == product.seller:
                raise serializers.ValidationError({
                    'product_id': "You cannot add your own products to cart"
                })
            
        except Product.DoesNotExist:
            pass  # Already handled in validate_product_id
        
        return data


# =========================
# UPDATE CART ITEM SERIALIZER
# =========================
class UpdateCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=0)

    def validate_quantity(self, value):
        if value > CartItem.MAX_QUANTITY_PER_ITEM:
            raise serializers.ValidationError(
                f"Maximum {CartItem.MAX_QUANTITY_PER_ITEM} units allowed per item"
            )
        return value

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value

    def validate(self, data):
        """Validate quantity against stock"""
        try:
            product = Product.objects.get(id=data['product_id'])
            quantity = data['quantity']
            
            # If quantity is not 0, check stock
            if quantity > 0 and quantity > product.stock:
                raise serializers.ValidationError({
                    'quantity': f"Only {product.stock} unit(s) available"
                })
            
        except Product.DoesNotExist:
            pass  # Already handled in validate_product_id
        
        return data


# =========================
# REMOVE FROM CART SERIALIZER
# =========================
class RemoveFromCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value


# =========================
# CART AUDIT LOG SERIALIZER
# =========================
class CartAuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = CartAuditLog
        fields = [
            'id', 'user', 'action', 'action_display', 
            'product_name', 'changes', 'timestamp', 'ip_address'
        ]
        read_only_fields = '__all__'


# =========================
# CART SUMMARY SERIALIZER (lightweight)
# =========================
class CartSummarySerializer(serializers.ModelSerializer):
    """Lightweight cart summary for quick checks"""
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = ['id', 'total_items', 'subtotal']
        read_only_fields = fields