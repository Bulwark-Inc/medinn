import api from '@/utils/api';

/**
 * Logs in the user and stores the access token.
 */
export const login = async (email, password) => {
  try {
    const res = await api.post('/auth/login/', { email, password });
    const accessToken = res.data.access;

    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
    }

    // Optionally fetch user details right after login
    const userRes = await api.get('/auth/me/');
    return userRes.data;
  } catch (error) {
    console.error('Login failed:', error?.response?.data || error.message);
    throw error;
  }
};

/**
 * Registers a new user.
 */
export const register = async (userData) => {
  try {
    const res = await api.post('/auth/register/', userData);
    return res.data;
  } catch (error) {
    console.error('Registration failed:', error?.response?.data || error.message);
    throw error;
  }
};

/**
 * Logs out the current user.
 */
export const logout = async () => {
  try {
    await api.post('/auth/logout/');
    localStorage.removeItem('access_token');
  } catch (error) {
    console.error('Logout failed:', error?.response?.data || error.message);
    throw error;
  }
};

/**
 * Fetches the currently authenticated user's data.
 */
export const getCurrentUser = async () => {
  try {
    const res = await api.get('/auth/me/');
    return res.data;
  } catch (error) {
    console.error('Failed to fetch user:', error?.response?.data || error.message);
    throw error;
  }
};

/**
 * Resends the verification email.
 */
export const resendVerificationEmail = async (email) => {
  try {
    const res = await api.post('/auth/resend-email-verification/', { email });
    return res.data;
  } catch (error) {
    console.error('Resend verification failed:', error?.response?.data || error.message);
    throw error;
  }
};

/**
 * Initiates password reset by sending an email.
 */
export const forgotPassword = async (email) => {
  try {
    const res = await api.post('/auth/forgot-password/', { email });
    return res.data;
  } catch (error) {
    console.error('Forgot password failed:', error?.response?.data || error.message);
    throw error;
  }
};

/**
 * Completes password reset.
 */
export const resetPassword = async (token, newPassword) => {
  try {
    const res = await api.post('/auth/reset-password/', {
      token,
      new_password: newPassword,
    });
    return res.data;
  } catch (error) {
    console.error('Reset password failed:', error?.response?.data || error.message);
    throw error;
  }
};
