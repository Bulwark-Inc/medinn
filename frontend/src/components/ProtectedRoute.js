'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

/**
 * ProtectedRoute component - Wraps pages that require authentication
 * and additional checks like email verification and seller status.
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - The protected content
 * @param {boolean} [props.requireEmailVerification=false] - If true, user must have verified email.
 * @param {boolean} [props.requireSeller=false] - If true, user must be a seller.
 * @param {string} [props.redirectTo='/login'] - Where to redirect if not authenticated.
 */
export default function ProtectedRoute({
  children,
  requireEmailVerification = false,
  requireSeller = false,
  redirectTo = '/login'
}) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return; // Don't redirect while loading

    // Not authenticated - redirect to login
    if (!isAuthenticated) {
      router.push(redirectTo);
      return;
    }

    // Email verification required but not verified
    if (requireEmailVerification && user && !user.email_verified) {
      // Optionally, you could redirect to a verification page or show a banner
      return;
    }

    // Seller required but not a seller
    if (requireSeller && user && !user.is_seller) {
      router.push('/dashboard'); // Redirect non-sellers to dashboard
      return;
    }
  }, [isAuthenticated, user, isLoading, router, redirectTo, requireEmailVerification, requireSeller]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // If not authenticated or other checks failed, return null to trigger redirect
  if (!isAuthenticated || (requireEmailVerification && user && !user.email_verified) || (requireSeller && user && !user.is_seller)) {
    return null; // Will redirect in useEffect
  }

  // All checks passed - render children
  return <>{children}</>;
}
