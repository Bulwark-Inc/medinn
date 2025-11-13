import axios from 'axios';

// 1. Initialize a base axios instance (with credentials)
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/',
  withCredentials: true, // Send cookies with requests (refresh token, etc.)
});

// 2. Initialize a separate, simple axios instance for the refresh request
//    It has the same baseURL and credentials but NO interceptors attached.
const refreshApi = axios.create({
  baseURL: 'http://localhost:8000/api/v1/',
  withCredentials: true,
});

// Interceptor for adding token to headers (Only runs on 'api' requests)
api.interceptors.request.use(
  (config) => {
    // We can add a check to explicitly skip headers for a specific path 
    // or flag, but simply using a separate instance is cleaner.
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Token refresh logic
api.interceptors.response.use(
  (response) => response, // Return the response if it's successful
  async (error) => {
    const originalRequest = error.config;
    // Check if the error is 401 AND it hasn't been retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        // *** FIX: Use the 'refreshApi' instance here! ***
        // It does not have the request interceptor, so no Authorization header is added.
        const res = await refreshApi.post('/auth/token/refresh/', {});

        const newAccessToken = res.data.access;
        localStorage.setItem('access_token', newAccessToken);

        // Retry the original request with the new access token
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;
        // The retry will use the 'api' instance, so it will pass through 
        // the request interceptor and use the new token.
        return api(originalRequest); 
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Optional: Redirect to login or clear auth state on refresh failure
      }
    }

    return Promise.reject(error);
  }
);

export default api;