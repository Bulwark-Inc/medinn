import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1/', // ✅ corrected base URL
  withCredentials: true, // ✅ send cookies (refresh token)
});

// Interceptor to inject token into headers
api.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      config.headers['Authorization'] = `Bearer ${accessToken}`; // Include token in headers
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor to handle token refreshing
api.interceptors.response.use(
  response => response, // Return the response if it's successful
  async error => {
    const originalRequest = error.config;

    // Check if the error is a 401 Unauthorized and if the token hasn't been refreshed yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Remove expired access token from localStorage before refreshing
        localStorage.removeItem('access_token');

        // Send refresh request without the Authorization header
        const res = await api.post('/auth/token/refresh/', {}, { headers: {} });

        const newAccessToken = res.data.access;
        
        // Store the new access token in localStorage
        localStorage.setItem('access_token', newAccessToken);

        // Update the authorization header for the original request with the new access token
        originalRequest.headers['Authorization'] = `Bearer ${newAccessToken}`;

        // Retry the original request with the new access token
        return api(originalRequest);
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
        // Optionally log the user out if refresh fails
        // e.g., logout();
      }
    }

    return Promise.reject(error);
  }
);

export default api;
