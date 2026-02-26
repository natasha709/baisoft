/**
 * API Client Configuration for Product Marketplace
 * ===============================================
 * 
 * This module configures Axios HTTP client for communicating with the Django backend.
 * It handles authentication, token management, and automatic token refresh.
 * 
 * Key Features:
 * - Automatic JWT token attachment to requests
 * - Token refresh on 401 errors (expired tokens)
 * - Request/response interceptors for global handling
 * - Environment-based API URL configuration
 * - Automatic logout on authentication failures
 * 
 * Authentication Flow:
 * 1. User logs in and receives access + refresh tokens
 * 2. Access token is attached to all API requests
 * 3. When access token expires (401 error), automatically refresh
 * 4. If refresh fails, logout user and redirect to login
 * 
 * Security Features:
 * - Tokens stored in localStorage (consider httpOnly cookies for production)
 * - Automatic token cleanup on authentication failure
 * - Request retry mechanism for expired tokens
 * - CSRF protection through proper headers
 */

import axios from 'axios';

// API base URL from environment variables with fallback for development
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

/**
 * Main API client instance with base configuration
 * 
 * This Axios instance is pre-configured with:
 * - Base URL pointing to Django backend
 * - JSON content type headers
 * - Request/response interceptors for authentication
 */
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout for requests
});

/**
 * Request Interceptor - Attach JWT Token
 * 
 * This interceptor runs before every request and automatically
 * attaches the JWT access token to the Authorization header.
 * 
 * Process:
 * 1. Check if we're in browser environment (not SSR)
 * 2. Get access token from localStorage
 * 3. Attach token to Authorization header if available
 * 4. Continue with request
 */
api.interceptors.request.use(
  (config) => {
    // Only access localStorage in browser environment
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    // Handle request setup errors
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor - Handle Token Refresh
 * 
 * This interceptor handles authentication errors and automatically
 * refreshes expired tokens without user intervention.
 * 
 * Process:
 * 1. If request succeeds, pass through response
 * 2. If request fails with 401 (unauthorized):
 *    a. Check if this is a retry attempt
 *    b. Try to refresh the access token using refresh token
 *    c. Update stored access token
 *    d. Retry original request with new token
 * 3. If refresh fails, logout user and redirect to login
 */
api.interceptors.response.use(
  // Success response - pass through unchanged
  (response) => response,
  
  // Error response - handle authentication errors
  async (error) => {
    const originalRequest = error.config;

    // Check if this is an authentication error and not already a retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true; // Mark as retry to prevent infinite loops

      try {
        // Attempt to refresh the access token
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (refreshToken) {
          // Call token refresh endpoint
          const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
            refresh: refreshToken,
          });
          
          // Extract new access token from response
          const { access } = response.data;
          
          // Update stored access token
          localStorage.setItem('access_token', access);
          
          // Update the failed request with new token and retry
          originalRequest.headers.Authorization = `Bearer ${access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed - user needs to login again
        console.error('Token refresh failed:', refreshError);
        
        // Clean up stored tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Redirect to login page
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      }
    }

    // For all other errors, pass through unchanged
    return Promise.reject(error);
  }
);

export default api;
