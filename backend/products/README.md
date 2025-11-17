# Products App Documentation

## Overview
The Products app handles all product-related functionality including product management, categories, reviews, and ratings for the e-commerce platform.

---

## Table of Contents
1. [Features](#features)
2. [Models](#models)
3. [API Endpoints](#api-endpoints)
4. [Permissions](#permissions)
5. [Usage Examples](#usage-examples)
6. [Validation Rules](#validation-rules)
7. [Setup & Configuration](#setup--configuration)

---

## Features

### Core Features
- ✅ Product CRUD operations (Create, Read, Update, Delete)
- ✅ Multiple images per product
- ✅ Nested category system
- ✅ Product reviews and ratings
- ✅ Review replies (seller responses)
- ✅ Helpful vote system for reviews
- ✅ Soft delete for products
- ✅ Stock management with low-stock alerts
- ✅ Auto-deactivation when out of stock
- ✅ Audit logging for all product changes
- ✅ Bulk operations
- ✅ Advanced filtering, search, and sorting
- ✅ Pagination

### Business Rules
- Only sellers can create/edit products
- Sellers can only manage their own products
- Users cannot review their own products
- Only product sellers can reply to reviews
- Verified purchase badge for reviews (integrated with orders)
- Products auto-deactivate when stock reaches 0
- Maximum 10 images per product

---

## Models

### 1. Category
Hierarchical category system with parent-child relationships.

```python
Category
├── id (PK)
├── name (unique)
├── slug (auto-generated)
├── parent (FK to self, nullable)
├── is_active
└── created_at
```

### 2. Product
Main product model with soft delete support.

```python
Product
├── id (PK)
├── seller (FK to User)
├── category (FK to Category)
├── name
├── slug (auto-generated)
├── description
├── price
├── stock
├── low_stock_threshold (default: 10)
├── is_active
├── is_deleted (soft delete)
├── deleted_at
├── created_at
└── updated_at

Properties:
├── is_low_stock (stock > 0 and stock <= threshold)
└── is_available (is_active and not is_deleted and stock > 0)
```

### 3. ProductImage
Multiple images per product with ordering.

```python
ProductImage
├── id (PK)
├── product (FK to Product)
├── image (ImageField)
├── alt_text
├── is_primary
├── order
└── created_at

Constraints:
├── Max 5MB per image
├── Auto-resize to 1920x1920
└── Only one primary image per product
```

### 4. ProductReview
Customer reviews with ratings.

```python
ProductReview
├── id (PK)
├── product (FK to Product)
├── user (FK to User)
├── rating (1-5)
├── title
├── content
├── image (optional)
├── is_verified (from orders)
├── created_at
└── updated_at

Constraints:
├── unique_together: (product, user)
└── User cannot review own products
```

### 5. ReviewReply
Seller responses to reviews.

```python
ReviewReply
├── id (PK)
├── review (FK to ProductReview)
├── user (FK to User)
├── content
├── created_at
└── updated_at

Constraints:
└── Only product seller can reply
```

### 6. ReviewHelpfulVote
Users can mark reviews as helpful.

```python
ReviewHelpfulVote
├── id (PK)
├── review (FK to ProductReview)
├── user (FK to User)
├── is_helpful
└── created_at

Constraints:
└── unique_together: (review, user)
```

### 7. ProductAuditLog
Tracks all product changes.

```python
ProductAuditLog
├── id (PK)
├── product (FK to Product)
├── user (FK to User)
├── action (CREATE, UPDATE, DELETE, RESTORE, STOCK_CHANGE)
├── changes (JSONField)
├── timestamp
└── ip_address
```

---

## API Endpoints

### Base URL: `/api/products/`

### Categories

#### List Categories
```http
GET /api/products/categories/
```
**Response:**
```json
{
  "success": true,
  "message": "Categories retrieved successfully",
  "data": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "parent": null,
      "is_active": true,
      "subcategories": [
        {
          "id": 2,
          "name": "Phones",
          "slug": "phones",
          "parent": 1,
          "is_active": true,
          "subcategories": [],
          "product_count": 15
        }
      ],
      "product_count": 45
    }
  ]
}
```

#### Get Category Detail
```http
GET /api/products/categories/{id}/
```

---

### Products

#### List Products
```http
GET /api/products/products/
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 12, max: 100)
- `min_price` - Minimum price filter
- `max_price` - Maximum price filter
- `min_rating` - Minimum average rating (1-5)
- `in_stock` - Filter in-stock products (true/false)
- `category` - Category ID
- `search` - Search in name, description, category
- `ordering` - Sort by: `price`, `-price`, `created_at`, `-created_at`, `average_rating`, `-average_rating`, `stock`

**Example:**
```http
GET /api/products/products/?min_price=10&max_price=100&category=1&ordering=-average_rating&page=1
```

**Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "count": 100,
    "next": "http://api/products/products/?page=2",
    "previous": null,
    "results": [
      {
        "id": 1,
        "seller": "john_seller",
        "category": {
          "id": 1,
          "name": "Electronics",
          "slug": "electronics"
        },
        "name": "Smartphone XYZ",
        "slug": "smartphone-xyz",
        "description": "Latest smartphone...",
        "price": "599.99",
        "stock": 50,
        "low_stock_threshold": 10,
        "primary_image": "http://example.com/media/products/phone.jpg",
        "is_active": true,
        "is_low_stock": false,
        "is_available": true,
        "average_rating": 4.5,
        "review_count": 23,
        "created_at": "2025-11-15T10:00:00Z",
        "updated_at": "2025-11-15T10:00:00Z"
      }
    ]
  }
}
```

#### Get Product Detail
```http
GET /api/products/products/{id}/
```

**Response:**
```json
{
  "success": true,
  "message": "Success",
  "data": {
    "id": 1,
    "seller": "john_seller",
    "seller_id": 5,
    "category": {...},
    "name": "Smartphone XYZ",
    "slug": "smartphone-xyz",
    "description": "Full description...",
    "price": "599.99",
    "stock": 50,
    "low_stock_threshold": 10,
    "images": [
      {
        "id": 1,
        "image": "http://example.com/media/products/phone1.jpg",
        "alt_text": "Front view",
        "is_primary": true,
        "order": 0
      },
      {
        "id": 2,
        "image": "http://example.com/media/products/phone2.jpg",
        "alt_text": "Back view",
        "is_primary": false,
        "order": 1
      }
    ],
    "is_active": true,
    "is_low_stock": false,
    "is_available": true,
    "average_rating": 4.5,
    "review_count": 23,
    "created_at": "2025-11-15T10:00:00Z",
    "updated_at": "2025-11-15T10:00:00Z"
  }
}
```

#### Create Product
```http
POST /api/products/products/
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Body:**
```json
{
  "category_id": 1,
  "name": "New Product",
  "description": "Product description",
  "price": 99.99,
  "stock": 100,
  "low_stock_threshold": 10,
  "is_active": true,
  "uploaded_images": [file1, file2, file3]
}
```

**Permissions:** Must be a seller

#### Update Product
```http
PUT /api/products/products/{id}/
PATCH /api/products/products/{id}/
Authorization: Bearer {token}
```

**Body:** (same as create, all fields optional for PATCH)

**Permissions:** Must be product owner

#### Delete Product (Soft Delete)
```http
DELETE /api/products/products/{id}/
Authorization: Bearer {token}
```

**Permissions:** Must be product owner

**Response:**
```json
{
  "success": true,
  "message": "Product deleted successfully"
}
```

#### Get My Products
```http
GET /api/products/products/my_products/
Authorization: Bearer {token}
```

Returns all products owned by authenticated seller.

**Permissions:** Must be a seller

#### Bulk Delete Products
```http
POST /api/products/products/bulk_delete/
Authorization: Bearer {token}
```

**Body:**
```json
{
  "product_ids": [1, 2, 3, 4, 5]
}
```

**Constraints:**
- Maximum 50 products at once
- Only your own products

**Response:**
```json
{
  "success": true,
  "message": "5 product(s) deleted successfully",
  "data": {
    "deleted_count": 5
  }
}
```

#### Add Images to Product
```http
POST /api/products/products/{id}/add_images/
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Body:**
```
images: [file1, file2, file3]
```

**Constraints:**
- Maximum 10 images per upload
- Maximum 10 total images per product
- Each image max 5MB

**Permissions:** Must be product owner

#### Delete Product Image
```http
DELETE /api/products/products/{id}/delete_image/
Authorization: Bearer {token}
```

**Body:**
```json
{
  "image_id": 5
}
```

**Permissions:** Must be product owner

#### Get Product Audit Logs
```http
GET /api/products/products/{id}/audit_logs/
Authorization: Bearer {token}
```

**Permissions:** Must be product owner

**Response:**
```json
{
  "success": true,
  "message": "Audit logs retrieved successfully",
  "data": [
    {
      "id": 1,
      "user": "john_seller",
      "action": "UPDATE",
      "action_display": "Updated",
      "changes": {
        "price": {
          "old": "99.99",
          "new": "89.99"
        }
      },
      "timestamp": "2025-11-15T10:00:00Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

---

### Reviews

#### List Reviews
```http
GET /api/products/reviews/
```

**Query Parameters:**
- `page` - Page number
- `page_size` - Items per page (default: 10, max: 50)
- `product` - Filter by product ID
- `rating` - Filter by rating (1-5)
- `verified` - Filter verified reviews (true/false)
- `ordering` - Sort by: `created_at`, `-created_at`, `rating`, `-rating`, `helpful_count`, `-helpful_count`

**Example:**
```http
GET /api/products/reviews/?product=1&ordering=-helpful_count
```

#### Create Review
```http
POST /api/products/reviews/
Authorization: Bearer {token}
Content-Type: multipart/form-data
```

**Body:**
```json
{
  "product": 1,
  "rating": 5,
  "title": "Great product!",
  "content": "I love this product because...",
  "image": file (optional)
}
```

**Constraints:**
- One review per user per product
- Cannot review own products
- Rating must be 1-5
- Image max 5MB

#### Update Review
```http
PUT /api/products/reviews/{id}/
PATCH /api/products/reviews/{id}/
Authorization: Bearer {token}
```

**Permissions:** Must be review owner

#### Delete Review
```http
DELETE /api/products/reviews/{id}/
Authorization: Bearer {token}
```

**Permissions:** Must be review owner

#### Vote Review as Helpful
```http
POST /api/products/reviews/{id}/vote_helpful/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "message": "Marked as helpful",
  "data": {
    "is_helpful": true
  }
}
```

**Note:** Calling again toggles the vote.

---

### Review Replies

#### List Replies
```http
GET /api/products/replies/
```

**Query Parameters:**
- `review` - Filter by review ID

#### Create Reply
```http
POST /api/products/replies/
Authorization: Bearer {token}
```

**Body:**
```json
{
  "review": 1,
  "content": "Thank you for your feedback!"
}
```

**Permissions:** Must be the product seller

---

## Permissions

### Product Management
- **Create:** Must be authenticated seller
- **Read:** Anyone (public)
- **Update:** Must be product owner
- **Delete:** Must be product owner

### Reviews
- **Create:** Authenticated users (except product seller)
- **Read:** Anyone
- **Update/Delete:** Review owner only

### Review Replies
- **Create:** Product seller only
- **Read:** Anyone

---

## Usage Examples

### Frontend Integration

#### Fetch Products with Filters
```javascript
// React example
const fetchProducts = async () => {
  const params = new URLSearchParams({
    category: 1,
    min_price: 10,
    max_price: 100,
    ordering: '-average_rating',
    page: 1
  });
  
  const response = await fetch(`/api/products/products/?${params}`);
  const data = await response.json();
  
  if (data.success) {
    setProducts(data.data.results);
  }
};
```

#### Create Product (Seller)
```javascript
const createProduct = async (formData) => {
  const form = new FormData();
  form.append('category_id', 1);
  form.append('name', 'New Product');
  form.append('description', 'Description');
  form.append('price', 99.99);
  form.append('stock', 100);
  
  // Add multiple images
  images.forEach(image => {
    form.append('uploaded_images', image);
  });
  
  const response = await fetch('/api/products/products/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: form
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Product created:', data.data);
  }
};
```

#### Submit Review
```javascript
const submitReview = async (productId, rating, title, content) => {
  const response = await fetch('/api/products/reviews/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      product: productId,
      rating,
      title,
      content
    })
  });
  
  const data = await response.json();
  if (data.success) {
    console.log('Review submitted:', data.data);
  } else {
    console.error('Error:', data.message, data.errors);
  }
};
```

---

## Validation Rules

### Products
- ✅ Price must be > 0
- ✅ Stock cannot be negative
- ✅ Category must be active
- ✅ Maximum 10 images per product
- ✅ Each image max 5MB
- ✅ Allowed formats: JPEG, PNG, WebP
- ✅ Auto-resize to 1920x1920

### Reviews
- ✅ Rating must be 1-5
- ✅ One review per user per product
- ✅ Cannot review own products
- ✅ Review image max 5MB

### Replies
- ✅ Only product seller can reply
- ✅ Content is required

---

## Setup & Configuration

### 1. Install Dependencies
```bash
pip install Pillow django-autoslug django-filter djangorestframework
```

### 2. Settings Configuration
```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'django_filters',
    'products',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 3. URL Configuration
```python
# urls.py
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/products/', include('products.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Run Migrations
```bash
python manage.py makemigrations products
python manage.py migrate
```

### 5. Create Superuser & Test
```bash
python manage.py createsuperuser
python manage.py runserver
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

## Notes

1. **Soft Delete:** Products are soft-deleted (not permanently removed)
2. **Auto-deactivation:** Products auto-deactivate when stock = 0
3. **Price Changes:** Track price history through audit logs
4. **Image Optimization:** Images are auto-resized and compressed
5. **Verified Reviews:** Automatically marked when user purchases product (via orders integration)

---

## Support & Issues

For issues or questions, check:
- API documentation at `/api/docs/` (if using drf-spectacular)
- Audit logs for tracking changes
- Error responses for detailed validation messages
