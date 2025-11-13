'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  login as loginService,
  logout as logoutService,
  getCurrentUser,
  register as registerService,
} from '@/features/auth/services/authService';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Create authentication context with default values
const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: () => {},
  logout: () => {},
  register: () => {},
});

export const AuthProvider = ({ children }) => {
  const queryClient = useQueryClient();

  // Check if token exists in localStorage
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  // Fetch current user using React Query
  const { 
    data: user,
    isLoading, 
    isFetching,
    refetch, 
    isError
  } = useQuery({
    queryKey: ['currentUser'],
    queryFn: getCurrentUser,
    staleTime: 0,  // Always check for the latest user
    retry: 0,      // Don’t retry on error
    enabled: !!token, // Run if token exists
  });
  
  // Show loader while checking user on initial load
  const isInitialLoading = isLoading && isFetching;

  // Handle user login
  const loginMutation = useMutation({
    mutationFn: async ({ email, password }) => {
      const userData = await loginService(email, password);
      // Refresh user data after login
      await queryClient.invalidateQueries({ queryKey: ['currentUser'] });
      return userData;
    },
  });

  // Handle user logout
  const logout = async () => {
    await logoutService();
    // Clear user cache after logout
    queryClient.setQueryData(['currentUser'], null);
    await queryClient.invalidateQueries({ queryKey: ['currentUser'] });
  };

  // Simplified login wrapper
  const login = async (email, password) => {
    await loginMutation.mutateAsync({ email, password });
  };

  // Handle user registration
  const register = async (userData) => {
    await registerService(userData);
    // Optionally: login or refresh user after registration
  };
  
  // Determine authentication status
  const isAuthenticated = !!user;

  // Display loading state during initial user check
  if (isInitialLoading) {
    return <div>Loading App...</div>;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        isLoading: loginMutation.isPending, 
        login,
        logout,
        register,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

// Hook for accessing auth context
export const useAuth = () => useContext(AuthContext);
