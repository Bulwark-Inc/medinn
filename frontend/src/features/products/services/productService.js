import api from '@/utils/api';

// Fetch all products, supports filtering (e.g., by category, price, etc.)
export const getProducts = async (filters = {}) => {
  try {
    const response = await api.get('/products/products/', { params: filters });
    console.log('1. Fetched products:', response.data);
    // Backend doesn't wrap list response, return as is
    return response.data;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

// Fetch all categories
export const getCategories = async () => {
  try {
    const response = await api.get('/products/categories/');
    // Backend wraps category response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

// Fetch a specific product by its ID
export const getProductById = async (id) => {
  try {
    const response = await api.get(`/products/products/${id}/`);
    console.log('2. product response:', response.data);
    // Backend wraps detail response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error fetching product:', error);
    throw error;
  }
};

// Create a new product (authenticated as Seller/Admin)
export const createProduct = async (productData) => {
  try {
    // Convert to FormData for image upload support
    const formData = new FormData();
    
    // Add basic fields
    if (productData.name) formData.append('name', productData.name);
    if (productData.description) formData.append('description', productData.description);
    if (productData.price) formData.append('price', productData.price);
    if (productData.stock !== undefined) formData.append('stock', productData.stock);
    if (productData.category_id) formData.append('category_id', productData.category_id);
    if (productData.low_stock_threshold) formData.append('low_stock_threshold', productData.low_stock_threshold);
    if (productData.is_active !== undefined) formData.append('is_active', productData.is_active);
    
    // Add images if provided (multiple images support)
    if (productData.images && Array.isArray(productData.images)) {
      productData.images.forEach((image) => {
        formData.append('uploaded_images', image);
      });
    }

    const response = await api.post('/products/products/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error creating product:', error);
    throw error;
  }
};

// Update an existing product (authenticated as Seller/Admin)
export const updateProduct = async (id, productData) => {
  try {
    // Convert to FormData for image upload support
    const formData = new FormData();
    
    // Add basic fields (only include if they exist in productData)
    if (productData.name) formData.append('name', productData.name);
    if (productData.description) formData.append('description', productData.description);
    if (productData.price) formData.append('price', productData.price);
    if (productData.stock !== undefined) formData.append('stock', productData.stock);
    if (productData.category_id) formData.append('category_id', productData.category_id);
    if (productData.low_stock_threshold) formData.append('low_stock_threshold', productData.low_stock_threshold);
    if (productData.is_active !== undefined) formData.append('is_active', productData.is_active);
    
    // Add new images if provided
    if (productData.images && Array.isArray(productData.images)) {
      productData.images.forEach((image) => {
        formData.append('uploaded_images', image);
      });
    }

    const response = await api.patch(`/products/products/${id}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error updating product:', error);
    throw error;
  }
};

// Delete a product (authenticated as Seller/Admin)
export const deleteProduct = async (id) => {
  try {
    const response = await api.delete(`/products/products/${id}/`);
    // Backend wraps response in {success, message}
    return response.data;
  } catch (error) {
    console.error('Error deleting product:', error);
    throw error;
  }
};

// Add images to existing product
export const addProductImages = async (id, images) => {
  try {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append('images', image);
    });

    const response = await api.post(`/products/products/${id}/add_images/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error adding product images:', error);
    throw error;
  }
};

// Delete a product image
export const deleteProductImage = async (productId, imageId) => {
  try {
    const response = await api.delete(`/products/products/${productId}/delete_image/`, {
      data: { image_id: imageId }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error deleting product image:', error);
    throw error;
  }
};

// Get seller's products
export const getMyProducts = async (filters = {}) => {
  try {
    const response = await api.get('/products/products/my_products/', { params: filters });
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error fetching my products:', error);
    throw error;
  }
};

// Bulk delete products
export const bulkDeleteProducts = async (productIds) => {
  try {
    const response = await api.post('/products/products/bulk_delete/', {
      product_ids: productIds
    });
    return response.data;
  } catch (error) {
    console.error('Error bulk deleting products:', error);
    throw error;
  }
};