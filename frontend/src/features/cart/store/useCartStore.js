import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { cartService } from '../service/cartService';

/**
 * Cart Store using Zustand
 * Manages client-side cart state with server synchronization
 */

const useCartStore = create(
  devtools(
    persist(
      (set, get) => ({
        // State
        cart: null,
        items: [],
        isLoading: false,
        error: null,
        isInitialized: false,
        warnings: [], // For backend warnings

        // Computed values
        get totalItems() {
          return get().items.reduce((sum, item) => sum + item.quantity, 0);
        },

        get totalPrice() {
          return get().items.reduce((sum, item) => sum + item.total_price, 0);
        },

        // Check if cart has any issues
        get hasIssues() {
          const state = get();
          return state.cart?.has_unavailable_items || state.cart?.has_stock_issues || false;
        },

        // Actions
        /**
         * Fetch cart from server
         */
        fetchCart: async () => {
          set({ isLoading: true, error: null });
          try {
            const cartData = await cartService.getCart();
            set({
              cart: cartData,
              items: cartData.items || [],
              warnings: cartData.warnings || [],
              isLoading: false,
              isInitialized: true,
            });
            return cartData;
          } catch (error) {
            const errorMsg = error.response?.data?.message || 
                           error.response?.data?.detail || 
                           'Failed to fetch cart';
            set({
              error: errorMsg,
              isLoading: false,
              isInitialized: true,
            });
            throw error;
          }
        },

        /**
         * Fetch cart summary (lightweight for navbar)
         */
        fetchCartSummary: async () => {
          try {
            const summary = await cartService.getCartSummary();
            // Just update the counts, don't replace full cart
            set({
              cart: summary,
            });
            return summary;
          } catch (error) {
            console.error('Failed to fetch cart summary:', error);
            throw error;
          }
        },

        /**
         * Add item to cart
         * @param {number} productId - Product ID
         * @param {number} quantity - Quantity to add
         * @param {Object} productDetails - Optional product details for optimistic update
         */
        addItem: async (productId, quantity = 1, productDetails = null) => {
          const currentItems = get().items;

          // Optimistic update
          const existingItemIndex = currentItems.findIndex(
            (item) => item.product.id === productId
          );

          let optimisticItems;
          if (existingItemIndex > -1) {
            // Update existing item
            optimisticItems = currentItems.map((item, index) =>
              index === existingItemIndex
                ? {
                    ...item,
                    quantity: item.quantity + quantity,
                    total_price: parseFloat((
                      (item.quantity + quantity) * parseFloat(item.current_price || item.price_at_addition)
                    ).toFixed(2)),
                  }
                : item
            );
          } else {
            // Add new item (if we have product details)
            if (productDetails) {
              optimisticItems = [
                ...currentItems,
                {
                  id: Date.now(), // Temporary ID
                  product: productDetails,
                  quantity,
                  price_at_addition: productDetails.price,
                  current_price: productDetails.price,
                  total_price: parseFloat((productDetails.price * quantity).toFixed(2)),
                  price_changed: false,
                  is_available: productDetails.is_available,
                  has_sufficient_stock: true,
                },
              ];
            } else {
              optimisticItems = currentItems;
            }
          }

          set({ items: optimisticItems, isLoading: true, error: null });

          try {
            await cartService.addToCart(productId, quantity);
            
            // Refresh cart to get accurate data from server
            await get().fetchCart();
          } catch (error) {
            // Rollback on error
            const errorMsg = error.response?.data?.message || 
                           error.response?.data?.errors?.product_id?.[0] ||
                           error.response?.data?.errors?.quantity?.[0] ||
                           'Failed to add item';
            set({ 
              items: currentItems,
              error: errorMsg,
              isLoading: false,
            });
            throw error;
          }
        },

        /**
         * Remove item from cart
         * @param {number} productId - Product ID to remove
         */
        removeItem: async (productId) => {
          const currentItems = get().items;
          
          // Optimistic update
          const optimisticItems = currentItems.filter(
            (item) => item.product.id !== productId
          );
          set({ items: optimisticItems, isLoading: true, error: null });

          try {
            await cartService.removeFromCart(productId);
            set({ isLoading: false });
            
            // Refresh to update totals
            await get().fetchCart();
          } catch (error) {
            // Rollback on error
            const errorMsg = error.response?.data?.message || 
                           'Failed to remove item';
            set({ 
              items: currentItems,
              error: errorMsg,
              isLoading: false,
            });
            throw error;
          }
        },

        /**
         * Update item quantity
         * @param {number} productId - Product ID
         * @param {number} quantity - New quantity (exact value, not increment)
         */
        updateItem: async (productId, quantity) => {
          if (quantity < 0) {
            throw new Error('Quantity cannot be negative');
          }

          if (quantity === 0) {
            // Setting to 0 doesn't delete, but we can handle it specially
            return get().updateItemQuantity(productId, 0);
          }

          const currentItems = get().items;
          
          // Optimistic update
          const optimisticItems = currentItems.map((item) =>
            item.product.id === productId
              ? {
                  ...item,
                  quantity,
                  total_price: parseFloat((
                    parseFloat(item.current_price || item.price_at_addition) * quantity
                  ).toFixed(2)),
                }
              : item
          );
          set({ items: optimisticItems, isLoading: true, error: null });

          try {
            await cartService.updateCartItem(productId, quantity);
            
            // Refresh cart to get accurate data
            await get().fetchCart();
          } catch (error) {
            // Rollback on error
            const errorMsg = error.response?.data?.message || 
                           error.response?.data?.errors?.quantity?.[0] ||
                           'Failed to update item';
            set({ 
              items: currentItems,
              error: errorMsg,
              isLoading: false,
            });
            throw error;
          }
        },

        /**
         * Increment item quantity by 1
         * @param {number} productId - Product ID
         */
        incrementItem: async (productId) => {
          const item = get().items.find(i => i.product.id === productId);
          if (!item) return;
          
          const newQuantity = item.quantity + 1;
          if (newQuantity > 99) {
            set({ error: 'Maximum quantity is 99' });
            return;
          }
          
          return get().updateItem(productId, newQuantity);
        },

        /**
         * Decrement item quantity by 1
         * @param {number} productId - Product ID
         */
        decrementItem: async (productId) => {
          const item = get().items.find(i => i.product.id === productId);
          if (!item) return;
          
          const newQuantity = item.quantity - 1;
          if (newQuantity <= 0) {
            // Ask user if they want to remove
            return get().removeItem(productId);
          }
          
          return get().updateItem(productId, newQuantity);
        },

        /**
         * Validate cart before checkout
         * @returns {Promise<{valid: boolean, issues?: array}>}
         */
        validateCart: async () => {
          set({ isLoading: true, error: null });
          try {
            const validation = await cartService.validateCart();
            set({ isLoading: false });
            
            if (!validation.valid && validation.issues) {
              // Set warning for user
              const issueMessages = validation.issues.map(
                issue => `${issue.product_name}: ${issue.issues.join(', ')}`
              );
              set({ warnings: issueMessages });
            }
            
            return validation;
          } catch (error) {
            const errorMsg = error.response?.data?.message || 
                           'Failed to validate cart';
            set({ 
              error: errorMsg,
              isLoading: false,
            });
            throw error;
          }
        },

        /**
         * Clear entire cart
         */
        clearCart: async () => {
          const currentState = { items: get().items, cart: get().cart };
          
          // Optimistic update
          set({ 
            items: [], 
            cart: null,
            isLoading: true, 
            error: null 
          });

          try {
            await cartService.clearCart();
            set({ isLoading: false });
          } catch (error) {
            // Rollback on error
            const errorMsg = error.response?.data?.message || 
                           'Failed to clear cart';
            set({ 
              items: currentState.items,
              cart: currentState.cart,
              error: errorMsg,
              isLoading: false,
            });
            throw error;
          }
        },

        /**
         * Clear cart locally (for logout)
         */
        clearCartLocal: () => {
          set({
            cart: null,
            items: [],
            isLoading: false,
            error: null,
            warnings: [],
            isInitialized: false,
          });
        },

        /**
         * Clear error state
         */
        clearError: () => {
          set({ error: null });
        },

        /**
         * Clear warnings
         */
        clearWarnings: () => {
          set({ warnings: [] });
        },
      }),
      {
        name: 'cart-storage', // localStorage key
        partialize: (state) => ({
          // Only persist items for offline viewing
          items: state.items,
        }),
      }
    ),
    {
      name: 'CartStore', // DevTools name
    }
  )
);

export default useCartStore;