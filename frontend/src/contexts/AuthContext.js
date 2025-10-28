'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  login as loginService,
  logout as logoutService,
  register as registerService,
  getCurrentUser,
  resendVerificationEmail as resendEmailService,
  forgotPassword as forgotPasswordService,
  resetPassword as resetPasswordService,
} from '@/features/auth/services/authService';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Fetch user on load
  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await getCurrentUser();
        setUser(currentUser);
      } catch {
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = async (email, password) => {
    const userData = await loginService(email, password);
    setUser(userData);
  };

  const logout = async () => {
    await logoutService();
    setUser(null);
  };

  const register = async (userData) => {
    await registerService(userData);
  };

  const resendVerificationEmail = async (email) => {
    await resendEmailService(email);
  };

  const forgotPassword = async (email) => {
    await forgotPasswordService(email);
  };

  const resetPassword = async (token, newPassword) => {
    await resetPasswordService(token, newPassword);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        register,
        resendVerificationEmail,
        forgotPassword,
        resetPassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
