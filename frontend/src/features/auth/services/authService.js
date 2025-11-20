import api from '@/utils/api';

/**
 * Logs in the user and stores the access token.
 * Backend returns: { access, user, message }
 * Refresh token is stored in httpOnly cookie automatically
 */
export const login = async (email, password) => {
  try {
    const res = await api.post('/accounts/login/', { email, password });
    const { access, user } = res.data;

    if (access) {
      localStorage.setItem('access_token', access);
    }

    return user;
  } catch (error) {
    // Handle specific error cases
    const errorData = error?.response?.data;
    
    if (errorData?.non_field_errors) {
      // Email not verified error
      if (errorData.non_field_errors[0]?.includes('Email is not verified')) {
        throw new Error('EMAIL_NOT_VERIFIED');
      }
      throw new Error(errorData.non_field_errors[0]);
    }
    
    if (errorData?.detail) {
      throw new Error(errorData.detail);
    }
    
    throw new Error('Login failed. Please check your credentials.');
  }
};

/**
 * Registers a new user.
 * Backend returns: { access, user, message }
 */
export const register = async (userData) => {
  try {
    const res = await api.post('/accounts/register/', userData);
    const { access, user, message } = res.data;

    // Store token if provided (user is logged in after registration)
    if (access) {
      localStorage.setItem('access_token', access);
    }

    return { user, message };
  } catch (error) {
    const errorData = error?.response?.data;
    
    // Handle validation errors
    if (errorData) {
      // Convert error object to readable message
      const errorMessages = Object.entries(errorData)
        .map(([key, value]) => {
          if (Array.isArray(value)) {
            return `${key}: ${value.join(', ')}`;
          }
          return `${key}: ${value}`;
        })
        .join('\n');
      
      throw new Error(errorMessages);
    }
    
    throw new Error('Registration failed. Please try again.');
  }
};

/**
 * Logs out the current user.
 * Blacklists the refresh token on the backend
 */
export const logout = async () => {
  try {
    await api.post('/accounts/logout/');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    // Always remove token from localStorage
    localStorage.removeItem('access_token');
  }
};

/**
 * Fetches the currently authenticated user's data.
 */
export const getCurrentUser = async () => {
  try {
    const res = await api.get('/accounts/me/');
    return res.data;
  } catch (error) {
    // If 401, token is invalid - remove it
    if (error?.response?.status === 401) {
      localStorage.removeItem('access_token');
    }
    throw error;
  }
};

/**
 * Refreshes the access token using the httpOnly refresh token cookie.
 * Backend automatically reads the refresh token from cookie.
 */
export const refreshAccessToken = async () => {
  try {
    const res = await api.post('/accounts/token/refresh/');
    const { access } = res.data;

    if (access) {
      localStorage.setItem('access_token', access);
    }

    return access;
  } catch (error) {
    // Refresh token is invalid or expired
    localStorage.removeItem('access_token');
    throw error;
  }
};

/**
 * Verifies email with token from the verification link.
 */
export const verifyEmail = async (token) => {
  try {
    const res = await api.post('/accounts/verify-email/', { token });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    throw new Error('Email verification failed. Token may be invalid or expired.');
  }
};

/**
 * Resends the verification email.
 */
export const resendVerificationEmail = async (email) => {
  try {
    const res = await api.post('/accounts/resend-email-verification/', { email });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    throw new Error('Failed to resend verification email.');
  }
};

/**
 * Initiates password reset by sending an email.
 */
export const forgotPassword = async (email) => {
  try {
    const res = await api.post('/accounts/forgot-password/', { email });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    throw new Error('Failed to send password reset email.');
  }
};

/**
 * Completes password reset using token and new password.
 */
export const resetPassword = async (token, newPassword, confirmPassword) => {
  try {
    const res = await api.post('/accounts/reset-password/', {
      token,
      new_password: newPassword,
      new_password2: confirmPassword,
    });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    if (errorData?.new_password) {
      throw new Error(errorData.new_password.join(', '));
    }
    
    throw new Error('Password reset failed. Token may be invalid or expired.');
  }
};

/**
 * Changes password for authenticated user.
 */
export const changePassword = async (oldPassword, newPassword, confirmPassword) => {
  try {
    const res = await api.post('/accounts/change-password/', {
      old_password: oldPassword,
      new_password: newPassword,
      new_password2: confirmPassword,
    });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.old_password) {
      throw new Error(errorData.old_password.join(', '));
    }
    
    if (errorData?.new_password) {
      throw new Error(errorData.new_password.join(', '));
    }
    
    throw new Error('Password change failed.');
  }
};

/**
 * Requests email change (sends verification to new email).
 */
export const requestEmailChange = async (newEmail, password) => {
  try {
    const res = await api.post('/accounts/request-email-change/', {
      new_email: newEmail,
      password,
    });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    throw new Error('Email change request failed.');
  }
};

/**
 * Verifies email change with token.
 */
export const verifyEmailChange = async (token) => {
  try {
    const res = await api.post('/accounts/verify-email-change/', { token });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    throw new Error('Email verification failed.');
  }
};

/**
 * Soft deletes the user account.
 */
export const deleteAccount = async (password) => {
  try {
    const res = await api.post('/accounts/delete-account/', { password });
    return res.data;
  } catch (error) {
    const errorData = error?.response?.data;
    
    if (errorData?.error) {
      throw new Error(errorData.error);
    }
    
    throw new Error('Account deletion failed.');
  }
};