# Carts App Documentation

## Overview
The Carts app manages shopping cart functionality with advanced features including price tracking, stock validation, and audit logging.

---

## Table of Contents
1. [Features](#features)
2. [Models](#models)
3. [API Endpoints](#api-endpoints)
4. [Usage Examples](#usage-examples)
5. [Validation Rules](#validation-rules)
6. [Setup & Configuration](#setup--configuration)

---

## Features

### Core Features
- ✅ Add/update/remove items from cart
- ✅ Price snapshot (tracks price at time of adding)
- ✅ Stock validation on all operations
- ✅ Price change detection
- ✅ Seller ownership prevention (can't buy own products)
- ✅ Maximum quantity limits (99 per item)
- ✅ Cart validation (availability, stock, price changes)
- ✅ Clear cart functionality
- ✅ Audit logging for all cart actions
- ✅ Transaction safety (atomic operations)
- ✅ Detailed product information in responses

### Business Rules
- Only authenticated users can have carts
- Maximum 99 units per cart item
- Sellers cannot add their own products to cart
- Products must be active and in stock
- Price is captured at time of adding (snapshot)
- Cart items show if price has changed since adding
- Quantity = 0 updates but doesn't delete (cleanup handled during checkout)

---

## Models

### 1. Cart
One cart per user.

```python
Cart
├── id (PK)
├── user (OneToOne to User)
├── created_at
└── updated_at

Properties:
├── total_items (sum of all quantities)
├── subtotal (sum of all item totals)
├── has_unavailable_items
└── has_stock_issues
```

### 2. CartItem
Items in the cart with price snapshots.

```python
CartItem
├── id (PK)
├── cart (FK to Cart)
├── product (FK to Product)
├── quantity (0-99)
├── price_at_addition (price snapshot)
├── created_at
└── updated_at

Properties:
├── total_price (price_at_addition * quantity)
├── current_price (product's current price)
├── price_changed (has price changed?)
├── price_difference (+ or -)
├── is_available (product still available?)
├── has_sufficient_stock (quantity <= stock?)
└── stock_status (in_stock, low_stock, insufficient_stock, unavailable)

Constraints:
├── unique_together: (cart, product)
├── Max quantity: 99
└── Cannot add seller's own products
```

### 3. CartAuditLog
Tracks all cart operations.

```python
CartAuditLog
├── id (PK)
├── cart (FK to Cart)
├── user (FK to User)
├── action (ADD, UPDATE, REMOVE, CLEAR)
├── product (FK to Product, nullable)
├── changes (JSONField)
├── timestamp
└── ip_address
```

---

## API Endpoints

### Base URL: `/api/cart/`

### Get Cart
```http
GET /api/cart/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Cart retrieved successfully",
  "data": {
    "id": 1,
    "user": "john_doe",
    "items": [
      {
        "id": 1,
        "product": {
          "id": 10,
          "name": "Smartphone XYZ",
          "slug": "smartphone-xyz",
          "price": "599.99",
          "stock": 50,
          "primary_image": "http://example.com/media/products/phone.jpg",
          "seller_name": "tech_store",
          "is_available": true,
          "is_low_stock": false
        },
        "quantity": 2,
        "price_at_addition": "599.99",
        "current_price": "599.99",
        "total_price": "1199.98",
        "price_changed": false,
        "price_difference": "0.00",
        "is_available": true,
        "has_sufficient_stock": true,
        "stock_status": "in_stock",
        "created_at": "2025-11-15T10:00:00Z",
        "updated_at": "2025-11-15T10:30:00Z"
      }
    ],
    "total_items": 2,
    "subtotal": "1199.98",
    "has_unavailable_items": false,
    "has_stock_issues": false,
    "created_at": "2025-11-15T09:00:00Z",
    "updated_at": "2025-11-15T10:30:00Z"
  },
  "warnings": []
}
```

**Warnings Array (if issues exist):**
```json
"warnings": [
  "Some items in your cart are no longer available",
  "Some items have insufficient stock"
]
```

---

### Get Cart Summary
```http
GET /api/cart/summary/
Authorization: Bearer {token}
```

Lightweight endpoint for quick cart info (e.g., navbar badge).

**Response:**
```json
{
  "success": true,
  "message": "Cart summary retrieved successfully",
  "data": {
    "id": 1,
    "total_items": 5,
    "subtotal": "499.95"
  }
}
```

---

### Add to Cart
```http
POST /api/cart/add/
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "product_id": 10,
  "quantity": 2
}
```

**Behavior:**
- If item doesn't exist: Creates new cart item
- If item exists: Adds to existing quantity
- Validates stock, max quantity, and seller ownership

**Response (Item Created):**
```json
{
  "success": true,
  "message": "Item added to cart successfully",
  "data": {
    "id": 1,
    "product": { ... },
    "quantity": 2,
    "price_at_addition": "599.99",
    "current_price": "599.99",
    "total_price": "1199.98",
    ...
  }
}
```

**Response (Quantity Updated):**
```json
{
  "success": true,
  "message": "Cart item quantity updated",
  "data": { ... }
}
```

**Error Examples:**
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "quantity": ["Only 3 unit(s) available"]
  }
}
```

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "product_id": ["You cannot add your own products to cart"]
  }
}
```

---

### Update Cart Item
```http
PATCH /api/cart/update/
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "product_id": 10,
  "quantity": 5
}
```

**Note:** 
- Sets quantity to exact value (not incremental)
- `quantity: 0` sets to 0 (doesn't delete)
- Validates against available stock

**Response:**
```json
{
  "success": true,
  "message": "Cart item updated successfully",
  "data": {
    "id": 1,
    "product": { ... },
    "quantity": 5,
    ...
  }
}
```

---

### Remove from Cart
```http
DELETE /api/cart/remove/
Authorization: Bearer {token}
Content-Type: application/json
```

**Body:**
```json
{
  "product_id": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Item removed from cart successfully"
}
```

---

### Clear Cart
```http
DELETE /api/cart/clear/
Authorization: Bearer {token}
```

Removes ALL items from cart.

**Response:**
```json
{
  "success": true,
  "message": "Cart cleared successfully",
  "data": {
    "items_removed": 5
  }
}
```

---

### Validate Cart
```http
GET /api/cart/validate/
Authorization: Bearer {token}
```

Checks all items for:
- Product availability
- Stock sufficiency
- Price changes

**Response (Valid Cart):**
```json
{
  "success": true,
  "message": "Cart is valid",
  "data": {
    "valid": true
  }
}
```

**Response (Issues Found):**
```json
{
  "success": true,
  "message": "Cart has validation issues",
  "data": {
    "valid": false,
    "issues": [
      {
        "product_id": 10,
        "product_name": "Smartphone XYZ",
        "issues": [
          "Price increased by 50.00",
          "Insufficient stock. Only 2 available"
        ]
      },
      {
        "product_id": 15,
        "product_name": "Laptop ABC",
        "issues": [
          "Product is no longer available"
        ]
      }
    ]
  }
}
```

**Use Case:** Call before checkout to warn users of any issues.

---

### Get Audit Logs
```http
GET /api/cart/audit-logs/
Authorization: Bearer {token}
```

Returns last 50 cart operations.

**Response:**
```json
{
  "success": true,
  "message": "Audit logs retrieved successfully",
  "data": [
    {
      "id": 1,
      "user": "john_doe",
      "action": "ADD",
      "action_display": "Item Added",
      "product_name": "Smartphone XYZ",
      "changes": {
        "quantity": 2,
        "price": "599.99"
      },
      "timestamp": "2025-11-15T10:00:00Z",
      "ip_address": "192.168.1.1"
    },
    {
      "id": 2,
      "user": "john_doe",
      "action": "UPDATE",
      "action_display": "Item Updated",
      "product_name": "Smartphone XYZ",
      "changes": {
        "old_quantity": 2,
        "new_quantity": 5
      },
      "timestamp": "2025-11-15T10:15:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

---

## Usage Examples

### Frontend Integration

#### Add to Cart
```javascript
// React example
const addToCart = async (productId, quantity = 1) => {
  try {
    const response = await fetch('/api/cart/add/', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        product_id: productId,
        quantity
      })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Show success message
      toast.success(data.message);
      // Update cart count
      updateCartCount();
    } else {
      // Show error
      toast.error(data.message);
      if (data.errors) {
        console.error('Validation errors:', data.errors);
      }
    }
  } catch (error) {
    console.error('Error adding to cart:', error);
  }
};
```

#### Update Quantity
```javascript
const updateQuantity = async (productId, newQuantity) => {
  const response = await fetch('/api/cart/update/', {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product_id: productId,
      quantity: newQuantity
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Update UI
    setCartItems(prevItems => 
      prevItems.map(item => 
        item.product.id === productId 
          ? { ...item, quantity: newQuantity }
          : item
      )
    );
  } else {
    alert(data.message);
  }
};
```

#### Remove Item
```javascript
const removeItem = async (productId) => {
  const response = await fetch('/api/cart/remove/', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product_id: productId
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Remove from UI
    setCartItems(prevItems => 
      prevItems.filter(item => item.product.id !== productId)
    );
  }
};
```

#### Validate Cart Before Checkout
```javascript
const validateCartBeforeCheckout = async () => {
  const response = await fetch('/api/cart/validate/', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  
  if (data.data.valid) {
    // Proceed to checkout
    navigate('/checkout');
  } else {
    // Show issues to user
    const issues = data.data.issues;
    issues.forEach(issue => {
      console.log(`${issue.product_name}:`, issue.issues);
      // Display warnings in UI
    });
  }
};
```

#### Display Cart with Price Change Warnings
```javascript
const CartItem = ({ item }) => {
  return (
    <div className="cart-item">
      <img src={item.product.primary_image} alt={item.product.name} />
      <div>
        <h3>{item.product.name}</h3>
        
        {/* Show price change warning */}
        {item.price_changed && (
          <div className="price-warning">
            {item.price_difference > 0 ? (
              <span className="text-red-500">
                Price increased by ${Math.abs(item.price_difference)}
              </span>
            ) : (
              <span className="text-green-500">
                Price decreased by ${Math.abs(item.price_difference)}
              </span>
            )}
          </div>
        )}
        
        {/* Show stock warning */}
        {!item.has_sufficient_stock && (
          <div className="text-red-500">
            Only {item.product.stock} available
          </div>
        )}
        
        {/* Show original price if changed */}
        <div>
          {item.price_changed && (
            <span className="line-through">${item.price_at_addition}</span>
          )}
          <span className="font-bold">${item.current_price}</span>
        </div>
        
        {/* Quantity controls */}
        <div>
          <button onClick={() => updateQuantity(item.product.id, item.quantity - 1)}>
            -
          </button>
          <span>{item.quantity}</span>
          <button onClick={() => updateQuantity(item.product.id, item.quantity + 1)}>
            +
          </button>
        </div>
        
        {/* Total */}
        <div>Total: ${item.total_price}</div>
      </div>
    </div>
  );
};
```

---

## Validation Rules

### Cart Items
- ✅ Product must exist and be active
- ✅ Product must not be deleted
- ✅ Product must be in stock
- ✅ Quantity must be 0-99
- ✅ Quantity cannot exceed available stock
- ✅ Cannot add seller's own products
- ✅ One unique product per cart (no duplicates)

### Operations
- ✅ Add: Validates stock before adding
- ✅ Update: Validates stock for new quantity
- ✅ Remove: Item must exist in cart
- ✅ All operations are atomic (transaction-safe)

---

## Error Handling

### Common Error Responses

#### Product Not Found
```json
{
  "success": false,
  "message": "Product not found or unavailable"
}
```

#### Insufficient Stock
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "quantity": ["Only 3 unit(s) available"]
  }
}
```

#### Max Quantity Exceeded
```json
{
  "success": false,
  "message": "Cannot add more. Maximum 99 units allowed per item"
}
```

#### Seller Ownership
```json
{
  "success": false,
  "message": "Validation failed",
  "errors": {
    "product_id": ["You cannot add your own products to cart"]
  }
}
```

#### Item Not in Cart
```json
{
  "success": false,
  "message": "Item not found in cart"
}
```

---

## Setup & Configuration

### 1. Install Dependencies
```bash
pip install djangorestframework
```

### 2. Settings Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'products',
    'carts',
]
```

### 3. URL Configuration
```python
# urls.py
urlpatterns = [
    path('api/cart/', include('carts.urls')),
]
```

### 4. Run Migrations
```bash
python manage.py makemigrations carts
python manage.py migrate
```

---

## Integration with Orders

When implementing the orders app, you'll need to:

### 1. Handle Cart Items with Quantity = 0
```python
# During order creation
cart.items.filter(quantity=0).delete()
```

### 2. Reduce Stock After Order
```python
# In orders app
with transaction.atomic():
    for cart_item in cart.items.all():
        product = Product.objects.select_for_update().get(
            id=cart_item.product_id
        )
        product.stock -= cart_item.quantity
        product.save()
```

### 3. Clear Cart After Successful Order
```python
# After payment confirmed
cart.clear()
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error message",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

---

## Stock Status Values

- `in_stock` - Product available with good stock
- `low_stock` - Product available but stock is low (≤ threshold)
- `insufficient_stock` - Quantity requested exceeds available stock
- `unavailable` - Product not available for purchase

---

## Notes

1. **Price Snapshots:** Cart items store the price when added. This prevents issues if sellers change prices.

2. **Quantity = 0:** Setting quantity to 0 doesn't delete the item. This allows users to "save for later" functionality. Cleanup happens during checkout.

3. **Transaction Safety:** All cart operations use database transactions to prevent race conditions.

4. **Audit Logging:** All cart changes are logged with IP addresses for security and debugging.

5. **Stock Validation:** Stock is validated on every add/update operation to prevent overselling.

6. **Seller Prevention:** Users cannot add their own products to cart (sellers can't buy from themselves).

---

## Performance Considerations

- Cart queries use `select_related()` and `prefetch_related()` for optimal performance
- Cart summary endpoint is lightweight for frequent calls (navbar badge)
- Atomic operations prevent race conditions during concurrent requests
- Indexes on (cart, product) for fast lookups

---

## Best Practices

1. **Always validate cart before checkout** using `/api/cart/validate/`
2. **Show price change warnings** to users in the UI
3. **Handle insufficient stock gracefully** by showing max available
4. **Update cart count** in navbar after add/update/remove operations
5. **Clear cart after successful order** to avoid confusion

---

## Support & Issues

For issues or questions:
- Check validation error messages in response
- Review audit logs for debugging
- Ensure products are active and not deleted
- Verify user is authenticated
