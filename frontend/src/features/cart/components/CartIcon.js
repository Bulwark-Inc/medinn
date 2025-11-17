'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import useCartStore from '../store/useCartStore';

export default function CartIcon() {
  const { user } = useAuth();
  const { totalItems, fetchCartSummary, clearCartLocal } = useCartStore();

  useEffect(() => {
    if (user) {
      // Fetch cart summary on mount
      fetchCartSummary().catch(console.error);
      
      // Optionally refresh every 30 seconds for real-time updates
      const interval = setInterval(() => {
        fetchCartSummary().catch(console.error);
      }, 30000);
      
      return () => clearInterval(interval);
    } else {
      // Clear cart when user logs out
      clearCartLocal();
    }
  }, [user, fetchCartSummary, clearCartLocal]);

  if (!user) {
    return (
      <Link
        href="/login"
        className="relative p-2 text-gray-700 hover:text-blue-600 transition-colors"
        aria-label="Login to view cart"
      >
        <svg
          className="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
          />
        </svg>
      </Link>
    );
  }

  return (
    <Link
      href="/cart"
      className="relative p-2 text-gray-700 hover:text-blue-600 transition-colors"
      aria-label={`Cart with ${totalItems} items`}
    >
      <svg
        className="w-6 h-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"
        />
      </svg>
      
      {/* Cart Badge */}
      {totalItems > 0 && (
        <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full h-5 w-5 flex items-center justify-center">
          {totalItems > 99 ? '99+' : totalItems}
        </span>
      )}
    </Link>
  );
}