import api from '@/utils/api';

// Fetch all products, supports filtering (e.g., by category, price, etc.)
export const getProducts = async (filters = {}) => {
  try {
    const response = await api.get('/products/products', { params: filters });
    return response.data.results;
  } catch (error) {
    console.error('Error fetching products:', error);
    throw error;
  }
};

// Fetch all categories
export const getCategories = async () => {
  try {
    const response = await api.get('/products/categories/');
    return response.data;
  } catch (error) {
    console.error('Error fetching categories:', error);
    throw error;
  }
};

// Fetch a specific product by its ID
export const getProductById = async (id) => {
  try {
    const response = await api.get(`/products/products/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error fetching product:', error);
    throw error;
  }
};

// Create a new product (authenticated as Seller/Admin)
export const createProduct = async (productData) => {
  try {
    const response = await api.post('/products/products/', productData);
    return response.data;
  } catch (error) {
    console.error('Error creating product:', error);
    throw error;
  }
};

// Update an existing product (authenticated as Seller/Admin)
export const updateProduct = async (id, productData) => {
  try {
    const response = await api.put(`/products/products/${id}/`, productData);
    return response.data;
  } catch (error) {
    console.error('Error updating product:', error);
    throw error;
  }
};

// Delete a product (authenticated as Seller/Admin)
export const deleteProduct = async (id) => {
  try {
    const response = await api.delete(`/products/products/${id}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting product:', error);
    throw error;
  }
};
