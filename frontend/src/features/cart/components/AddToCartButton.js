'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import useCartStore from '../store/useCartStore';

export default function AddToCartButton({ 
  product, 
  showQuantitySelector = false,
  variant = 'primary',
  className = '' 
}) {
  const { user } = useAuth();
  const router = useRouter();
  const { addItem, isLoading } = useCartStore();
  
  const [quantity, setQuantity] = useState(1);
  const [isAdding, setIsAdding] = useState(false);

  const handleAddToCart = async () => {
    if (!user) {
      router.push('/login?redirect=/products/' + product.slug);
      return;
    }

    if (!product.is_available) {
      alert('This product is currently out of stock');
      return;
    }

    if (quantity > product.stock) {
      alert(`Only ${product.stock} available in stock`);
      return;
    }

    setIsAdding(true);
    
    try {
      await addItem(product.id, quantity, {
        id: product.id,
        name: product.name,
        slug: product.slug,
        price: product.price,
        primary_image: product.primary_image,
        seller_name: product.seller || product.seller_name,
        is_available: product.is_available,
        is_low_stock: product.is_low_stock,
        stock: product.stock,
      });
      
      // Show success feedback
      if (showQuantitySelector) {
        alert(`${quantity} ${quantity === 1 ? 'item' : 'items'} added to cart!`);
      }
      
      // Reset quantity
      setQuantity(1);
    } catch (error) {
      const errorMsg = error.response?.data?.message || 
                      error.response?.data?.errors?.product_id?.[0] ||
                      error.response?.data?.errors?.quantity?.[0] ||
                      'Failed to add to cart';
      alert(errorMsg);
    } finally {
      setIsAdding(false);
    }
  };

  const incrementQuantity = () => {
    if (quantity < product.stock && quantity < 99) {
      setQuantity(quantity + 1);
    }
  };

  const decrementQuantity = () => {
    if (quantity > 1) {
      setQuantity(quantity - 1);
    }
  };

  // Button styles based on variant
  const buttonStyles = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800',
    secondary: 'bg-gray-800 text-white hover:bg-gray-900 active:bg-black',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50',
  };

  const selectedStyle = buttonStyles[variant] || buttonStyles.primary;

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Quantity Selector (if enabled) */}
      {showQuantitySelector && (
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Quantity:</label>
          <div className="flex items-center border border-gray-300 rounded-lg">
            <button
              onClick={decrementQuantity}
              disabled={quantity <= 1}
              type="button"
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              −
            </button>
            
            <input
              type="number"
              value={quantity}
              onChange={(e) => {
                const val = parseInt(e.target.value) || 1;
                if (val >= 1 && val <= Math.min(product.stock, 99)) {
                  setQuantity(val);
                }
              }}
              min="1"
              max={Math.min(product.stock, 99)}
              className="w-16 text-center border-0 focus:outline-none"
            />
            
            <button
              onClick={incrementQuantity}
              disabled={quantity >= product.stock || quantity >= 99}
              type="button"
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              +
            </button>
          </div>
          
          <span className="text-sm text-gray-600">
            {product.stock} available
          </span>
        </div>
      )}

      {/* Add to Cart Button */}
      <button
        onClick={handleAddToCart}
        disabled={isAdding || isLoading || !product.is_available}
        className={`
          w-full py-3 px-6 rounded-lg font-semibold
          transition-colors duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
          flex items-center justify-center gap-2
          ${selectedStyle}
        `}
      >
        {isAdding ? (
          <>
            <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            Adding...
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
              />
            </svg>
            {!product.is_available ? 'Out of Stock' : 'Add to Cart'}
          </>
        )}
      </button>

      {/* Stock Warning */}
      {product.is_available && product.is_low_stock && (
        <p className="text-sm text-orange-600 text-center">
          ⚠ Only {product.stock} left in stock
        </p>
      )}
    </div>
  );
}