# eCommerce Backend API - Products App Documentation

## Overview
This module is responsible for managing the product-related functionality in the eCommerce backend. It includes models for product listings, categories, product reviews, and review interactions (e.g., replies, helpful votes).

This app exposes the following features:

- Categories for organizing products.
- CRUD operations for products (create, read, update, delete).
- Product reviews with replies and helpful vote tracking.

## Models

### 1. Category Model
Represents product categories. A category can have subcategories, forming a tree structure.

- **Fields:**
  - `name`: Name of the category.
  - `slug`: Auto-generated slug based on the name.
  - `parent`: Self-referencing foreign key for subcategories.

### 2. Product Model
Represents individual products in the store. Each product is linked to a seller (user) and a category.

- **Fields:**
  - `seller`: Foreign key to the user who created the product.
  - `category`: Foreign key to the category.
  - `name`: Name of the product.
  - `slug`: Auto-generated slug based on the product name.
  - `description`: Detailed description of the product.
  - `price`: Price of the product.
  - `stock`: Available stock count.
  - `image`: Optional image field for the product.
  - `is_active`: Boolean to indicate if the product is active.
  - `created_at`: Timestamp when the product was created.
  - `updated_at`: Timestamp when the product was last updated.

### 3. ProductReview Model
Represents reviews for products. Each review has a rating, a title, and content, with optional media (images).

- **Fields:**
  - `product`: Foreign key to the associated product.
  - `user`: Foreign key to the user who created the review.
  - `rating`: Rating from 1 to 5.
  - `title`: Optional title of the review.
  - `content`: Review text content.
  - `image`: Optional image related to the review.
  - `is_verified`: Boolean to indicate if the review is verified (could be tied to orders).
  - `created_at`: Timestamp when the review was created.
  - `updated_at`: Timestamp when the review was last updated.

### 4. ReviewReply Model
Represents replies to product reviews, either from the product seller or other users.

- **Fields:**
  - `review`: Foreign key to the product review being replied to.
  - `user`: Foreign key to the user who created the reply.
  - `content`: Text content of the reply.
  - `created_at`: Timestamp when the reply was created.
  - `updated_at`: Timestamp when the reply was last updated.

### 5. ReviewHelpfulVote Model
Tracks helpful votes on reviews. Users can mark reviews as helpful or not helpful.

- **Fields:**
  - `review`: Foreign key to the product review.
  - `user`: Foreign key to the user who cast the vote.
  - `is_helpful`: Boolean indicating if the review was marked as helpful.
  - `created_at`: Timestamp when the vote was cast.

## Serializers

### 1. CategorySerializer
Serializes the `Category` model to return the category data in JSON format.

- **Fields:**
  - `id`
  - `name`
  - `slug`
  - `parent`

### 2. ProductSerializer
Serializes the `Product` model, including related category information and additional fields like average rating and review count.

- **Fields:**
  - `id`
  - `seller`
  - `category`
  - `name`
  - `slug`
  - `description`
  - `price`
  - `stock`
  - `image`
  - `is_active`
  - `average_rating`
  - `review_count`
  - `created_at`
  - `updated_at`

### 3. ProductReviewSerializer
Serializes the `ProductReview` model, including related reply data and helpful vote count.

- **Fields:**
  - `id`
  - `user`
  - `rating`
  - `title`
  - `content`
  - `image`
  - `is_verified`
  - `created_at`
  - `replies`
  - `helpful_count`

### 4. ReviewReplySerializer
Serializes the `ReviewReply` model.

- **Fields:**
  - `id`
  - `user`
  - `content`
  - `created_at`

### 5. ReviewHelpfulVoteSerializer
Serializes the `ReviewHelpfulVote` model.

- **Fields:**
  - `id`
  - `user`
  - `is_helpful`
  - `created_at`

## Views

### 1. CategoryViewSet
Handles CRUD operations for categories. This viewset supports **read-only** access for all users.

- **Permissions**: `AllowAny`
- **URLs**:
  - `GET /api/v1/products/categories/`: List all categories.
  - `GET /api/v1/products/categories/{id}/`: Get details of a single category.

### 2. ProductViewSet
Handles CRUD operations for products. Sellers can manage their products, while non-authenticated users can only view products.

- **Permissions**: `IsAuthenticatedOrReadOnly`
- **URLs**:
  - `GET /api/v1/products/products/`: List all active products.
  - `POST /api/v1/products/products/`: Create a new product (only for sellers).
  - `GET /api/v1/products/products/{id}/`: Get details of a single product.
  - `PUT /api/v1/products/products/{id}/`: Update a product (only by the seller).
  - `DELETE /api/v1/products/products/{id}/`: Delete a product (only by the seller).

### 3. ProductReviewViewSet
Handles CRUD operations for product reviews. Users can create reviews for products, as well as vote if a review was helpful.

- **Permissions**: `IsAuthenticatedOrReadOnly`
- **URLs**:
  - `GET /api/v1/products/reviews/`: List all reviews for products.
  - `POST /api/v1/products/reviews/`: Create a new review.
  - `GET /api/v1/products/reviews/{id}/`: Get a specific review.
  - `POST /api/v1/products/reviews/{id}/vote_helpful/`: Mark a review as helpful.

### 4. ReviewReplyViewSet
Handles CRUD operations for replies to product reviews.

- **Permissions**: `IsAuthenticatedOrReadOnly`
- **URLs**:
  - `GET /api/v1/products/replies/`: List all replies.
  - `POST /api/v1/products/replies/`: Create a new reply to a review.

### 5. ReviewHelpfulVoteViewSet
Handles CRUD operations for helpful votes on reviews.

- **Permissions**: `IsAuthenticated`
- **URLs**:
  - `GET /api/v1/products/votes/`: List all helpful votes.
  - `POST /api/v1/products/votes/`: Create a new helpful vote.

## Permissions
- **IsAuthenticatedOrReadOnly**: Allows read-only access to unauthenticated users (e.g., viewing products), but requires authentication for creating, updating, or deleting resources.
- **IsSeller**: A custom permission that restricts certain actions (e.g., creating or modifying products) to users who are sellers.

## URL Routing
The routes for the products app are defined in the `urls.py` file:

```python
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'reviews', ProductReviewViewSet, basename='review')
router.register(r'replies', ReviewReplyViewSet, basename='reply')
router.register(r'votes', ReviewHelpfulVoteViewSet, basename='vote')

urlpatterns = [
    path('', include(router.urls)),
]


# API Endpoints for Products (Samples)

## 1. API Endpoints

Based on the backend code, here are the relevant endpoints for managing products:

### `GET /products/`
- **Description**: Retrieve a list of active products.

### `GET /products/{id}/`
- **Description**: Retrieve a single product by its ID.

### `POST /products/`
- **Description**: Create a new product (only accessible by sellers).

### `PUT /products/{id}/`
- **Description**: Update an existing product (only accessible by the products seller or admins).

### `DELETE /products/{id}/`
- **Description**: Delete a product (only accessible by the products seller or admins).

## 2. Endpoint Parameters and Expected Data

### `GET /products/`

#### Query Parameters:

- `category`: Filter by category (optional).
- `min_price`: Minimum price for filtering products (optional).
- `max_price`: Maximum price for filtering products (optional).
- `min_rating`: Minimum average rating for filtering products (optional).
- `in_stock`: Filter to show products in stock (optional).
- `search`: Search products by name or description (optional).
- `ordering`: Define ordering, e.g., price, created_at, average_rating (optional).

### `POST /products/`

#### Request Body (to create a product):
```json
{
  "name": "Product Name",
  "description": "Product Description",
  "price": 100.00,
  "stock": 50,
  "category": 1,  // Category ID
  "image": "<file> (optional)",
  "is_active": true
}
```
- Note: The seller will be automatically assigned from the authenticated user.

### `GET /products/{id}/`

#### Response Body (Product data):
```json
{
  "id": 1,
  "name": "Product Name",
  "slug": "product-name",
  "description": "Product Description",
  "price": 100.00,
  "stock": 50,
  "category": { "id": 1, "name": "Category Name" },
  "seller": "seller_name",
  "average_rating": 4.5,
  "review_count": 20,
  "is_active": true,
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-10T00:00:00Z"
}
```

### `PUT /products/{id}/`

#### Request Body (to update a product):
```json
{
  "name": "Updated Product Name",
  "description": "Updated Product Description",
  "price": 120.00,
  "stock": 60,
  "category": 1,  // Category ID
  "image": "<file> (optional)",
  "is_active": true
}
```

### `DELETE /products/{id}/`

#### Request Body: No request body—just DELETE the product.
