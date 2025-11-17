import api from '@/utils/api';

/**
 * Cart Service
 * Handles all cart-related API calls with proper error handling
 */

export const cartService = {
  /**
   * Get current user's cart with full details
   * @returns {Promise} Cart data with items
   */
  getCart: async () => {
    const response = await api.get('/cart/');
    return response.data.data; // Extract 'data' from {success, message, data}
  },

  /**
   * Get cart summary (lightweight for navbar)
   * @returns {Promise} Cart summary with total_items and subtotal
   */
  getCartSummary: async () => {
    const response = await api.get('/cart/summary/');
    return response.data.data;
  },

  /**
   * Add item to cart or increase quantity
   * @param {number} productId - Product ID to add
   * @param {number} quantity - Quantity to add (default: 1)
   * @returns {Promise} Added/updated cart item
   */
  addToCart: async (productId, quantity = 1) => {
    const response = await api.post('/cart/add/', {
      product_id: productId,
      quantity,
    });
    return response.data.data;
  },

  /**
   * Remove item from cart completely
   * @param {number} productId - Product ID to remove
   * @returns {Promise} Success message
   */
  removeFromCart: async (productId) => {
    const response = await api.delete('/cart/remove/', {
      data: { product_id: productId } // DELETE requests need data in config
    });
    return response.data;
  },

  /**
   * Update cart item quantity (set to exact value)
   * @param {number} productId - Product ID to update
   * @param {number} quantity - New quantity (0 to hide, not delete)
   * @returns {Promise} Updated cart item
   */
  updateCartItem: async (productId, quantity) => {
    const response = await api.patch('/cart/update/', {
      product_id: productId,
      quantity,
    });
    return response.data.data;
  },

  /**
   * Clear entire cart
   * @returns {Promise} Success message with items_removed count
   */
  clearCart: async () => {
    const response = await api.delete('/cart/clear/');
    return response.data.data;
  },

  /**
   * Validate cart before checkout
   * Checks for availability, stock, and price changes
   * @returns {Promise} Validation result {valid: boolean, issues?: array}
   */
  validateCart: async () => {
    const response = await api.get('/cart/validate/');
    return response.data.data;
  },

  /**
   * Get cart audit logs (last 50 operations)
   * @returns {Promise} Array of audit log entries
   */
  getAuditLogs: async () => {
    const response = await api.get('/cart/audit-logs/');
    return response.data.data;
  },
};