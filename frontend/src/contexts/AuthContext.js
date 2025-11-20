'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  login as loginService,
  logout as logoutService,
  getCurrentUser,
  register as registerService,
  refreshAccessToken,
} from '@/features/auth/services/authService';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import useCartStore from '@/features/cart/store/useCartStore';

// Create authentication context with default values
const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  login: () => {},
  logout: () => {},
  register: () => {},
  refetchUser: () => {},
});

export const AuthProvider = ({ children }) => {
  const queryClient = useQueryClient();
  const [hasMounted, setHasMounted] = useState(false);
  const [authError, setAuthError] = useState(null);
  const clearCart = useCartStore((state) => state.clearCartLocal);

  // Check if token exists in localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  // Fetch current user using React Query
  const { 
    data: user,
    isLoading, 
    isFetching,
    refetch, 
    isError,
    error: queryError
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: (failureCount, error) => {
      // Don't retry on 401 (unauthorized)
      if (error?.response?.status === 401) {
        return false;
      }
      return failureCount < 2;
    },
    enabled: !!token, // Only run if token exists
  });
  
  // Show loader while checking user on initial load
  const isInitialLoading = isLoading && isFetching;

  // Handle automatic token refresh on 401 errors
  useEffect(() => {
    if (queryError?.response?.status === 401 && token) {
      // Try to refresh the token
      refreshAccessToken()
        .then(() => {
          // Refetch user after successful token refresh
          refetch();
        })
        .catch(() => {
          // Refresh failed, clear token and user
          localStorage.removeItem('access_token');
          queryClient.setQueryData(['currentUser'], null);
        });
    }
  }, [queryError, token, refetch, queryClient]);

  // Handle user login
  const loginMutation = useMutation({
    mutationFn: async ({ email, password }) => {
      setAuthError(null);
      const userData = await loginService(email, password);
      return userData;
    },
    onSuccess: async (userData) => {
      // Set user data immediately
      queryClient.setQueryData(['currentUser'], userData);
      // Invalidate to refetch fresh data
      await queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
    onError: (error) => {
      setAuthError(error.message);
    },
  });

  // Handle user registration
  const registerMutation = useMutation({
    mutationFn: async (userData) => {
      setAuthError(null);
      const result = await registerService(userData);
      return result;
    },
    onSuccess: async (result) => {
      // If user is logged in after registration, set user data
      if (result.user) {
        queryClient.setQueryData(['currentUser'], result.user);
        await queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      }
      return result;
    },
    onError: (error) => {
      setAuthError(error.message);
    },
  });

  // Handle user logout
  const logout = async () => {
    try {
      await logoutService();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear local state
      clearCart();
      queryClient.setQueryData(['currentUser'], null);
      await queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      setAuthError(null);
    }
  };

  // Simplified login wrapper
  const login = async (email, password) => {
    const result = await loginMutation.mutateAsync({ email, password });
    return result;
  };

  // Simplified register wrapper
  const register = async (userData) => {
    const result = await registerMutation.mutateAsync(userData);
    return result;
  };

  // Manual user refetch function
  const refetchUser = async () => {
    await refetch();
  };
  
  // Determine authentication status
  const isAuthenticated = !!user && !!token;
  
  useEffect(() => {
    // This runs only on the client after the initial render (hydration)
    setHasMounted(true);
  }, []);

  // Display loading state during initial user check
  if (!hasMounted || isInitialLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent"></div>
          <p className="mt-2 text-gray-600">Loading App...</p>
        </div>
      </div>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading: loginMutation.isPending || registerMutation.isPending,
        error: authError,
        login,
        logout,
        register,
        refetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Hook for accessing auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};