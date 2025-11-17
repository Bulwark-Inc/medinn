'use client';

import { useState } from 'react';
import Link from 'next/link';
import useCartStore from '../store/useCartStore';

export default function CartItem({ item }) {
  const { updateItem, removeItem, isLoading } = useCartStore();
  const [localQuantity, setLocalQuantity] = useState(item.quantity);
  const [isUpdating, setIsUpdating] = useState(false);

  const product = item.product_details || item.product;
  const productId = product?.id;

  // Handle quantity change with debounce
  const handleQuantityChange = async (newQuantity) => {
    if (newQuantity < 1) return;
    if (newQuantity > 99) {
      alert('Maximum quantity is 99');
      return;
    }

    setLocalQuantity(newQuantity);
    setIsUpdating(true);

    try {
      await updateItem(productId, newQuantity);
    } catch (error) {
      // Reset to original quantity on error
      setLocalQuantity(item.quantity);
      alert(error.response?.data?.message || 'Failed to update quantity');
    } finally {
      setIsUpdating(false);
    }
  };

  const handleRemove = async () => {
    if (confirm(`Remove ${product.name} from cart?`)) {
      setIsUpdating(true);
      try {
        await removeItem(productId);
      } catch (error) {
        alert('Failed to remove item');
        setIsUpdating(false);
      }
    }
  };

  // Calculate price display
  const priceChanged = item.price_changed;
  const priceDifference = parseFloat(item.price_difference || 0);
  const priceIncreased = priceDifference > 0;
  const priceDecreased = priceDifference < 0;

  return (
    <div className="flex gap-4 py-6 border-b border-gray-200 last:border-0">
      {/* Product Image */}
      <Link href={`/products/${product.slug}`} className="flex-shrink-0">
        <div className="w-24 h-24 bg-gray-200 rounded-lg overflow-hidden">
          {product.primary_image ? (
            <img
              src={product.primary_image}
              alt={product.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <span className="text-gray-400 text-xs">No image</span>
            </div>
          )}
        </div>
      </Link>

      {/* Product Details */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <Link
              href={`/products/${product.slug}`}
              className="text-lg font-semibold text-gray-900 hover:text-blue-600 transition-colors"
            >
              {product.name}
            </Link>

            {/* Seller */}
            {product.seller_name && (
              <p className="text-sm text-gray-500 mt-1">
                Sold by: {product.seller_name}
              </p>
            )}

            {/* Availability Warning */}
            {!item.is_available && (
              <div className="mt-2 flex items-center gap-1 text-red-600 text-sm font-medium">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                Product no longer available
              </div>
            )}

            {/* Stock Warning */}
            {item.is_available && !item.has_sufficient_stock && (
              <div className="mt-2 flex items-center gap-1 text-orange-600 text-sm font-medium">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                Only {product.stock} available
              </div>
            )}

            {/* Low Stock Warning */}
            {item.is_available && item.has_sufficient_stock && product.is_low_stock && (
              <div className="mt-2 flex items-center gap-1 text-yellow-600 text-sm">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                Low stock
              </div>
            )}

            {/* Price Info */}
            <div className="mt-3">
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold text-gray-900">
                  ${parseFloat(item.current_price).toFixed(2)}
                </span>
                
                {/* Show original price if changed */}
                {priceChanged && (
                  <span className="text-sm text-gray-500 line-through">
                    ${parseFloat(item.price_at_addition).toFixed(2)}
                  </span>
                )}
              </div>

              {/* Price Change Warning */}
              {priceChanged && (
                <div className="mt-1">
                  {priceIncreased && (
                    <span className="text-sm text-red-600 font-medium">
                      ↑ Price increased by ${Math.abs(priceDifference).toFixed(2)}
                    </span>
                  )}
                  {priceDecreased && (
                    <span className="text-sm text-green-600 font-medium">
                      ↓ Price decreased by ${Math.abs(priceDifference).toFixed(2)}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Item Total */}
          <div className="text-right ml-4">
            <p className="text-xl font-bold text-gray-900">
              ${parseFloat(item.total_price).toFixed(2)}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              ${parseFloat(item.current_price).toFixed(2)} × {item.quantity}
            </p>
          </div>
        </div>

        {/* Quantity Controls */}
        <div className="flex items-center gap-4 mt-4">
          <div className="flex items-center border border-gray-300 rounded-lg">
            <button
              onClick={() => handleQuantityChange(localQuantity - 1)}
              disabled={isUpdating || localQuantity <= 1 || !item.is_available}
              className="px-3 py-2 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              −
            </button>
            
            <input
              type="number"
              value={localQuantity}
              onChange={(e) => {
                const val = parseInt(e.target.value) || 1;
                if (val >= 1 && val <= 99) {
                  handleQuantityChange(val);
                }
              }}
              disabled={isUpdating || !item.is_available}
              min="1"
              max="99"
              className="w-16 text-center border-0 focus:outline-none disabled:bg-gray-50"
            />
            
            <button
              onClick={() => handleQuantityChange(localQuantity + 1)}
              disabled={isUpdating || localQuantity >= 99 || !item.is_available || !item.has_sufficient_stock}
              className="px-3 py-2 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              +
            </button>
          </div>

          {/* Remove Button */}
          <button
            onClick={handleRemove}
            disabled={isUpdating}
            className="text-sm text-red-600 hover:text-red-800 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isUpdating ? 'Removing...' : 'Remove'}
          </button>

          {/* Loading Indicator */}
          {isUpdating && (
            <div className="ml-2">
              <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}