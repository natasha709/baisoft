/**
 * Authentication Utilities for Product Marketplace
 * ===============================================
 * 
 * This module provides authentication functions and utilities for the frontend application.
 * It handles user login, registration, token management, and session persistence.
 * 
 * Key Features:
 * - JWT token-based authentication
 * - Local storage for session persistence
 * - User registration with business creation
 * - Role-based user management
 * - Session validation and user retrieval
 * 
 * Security Considerations:
 * - Tokens stored in localStorage (consider httpOnly cookies for production)
 * - Automatic token cleanup on logout
 * - Server-side validation for all operations
 * - Role-based access control support
 * 
 * Integration:
 * - Works with API client (./api.ts) for HTTP requests
 * - Used by AuthContext for global state management
 * - Supports Next.js SSR with window checks
 */

import api from './api';

/**
 * User Interface Definition
 * 
 * Represents a user in the system with role-based permissions.
 * This interface matches the backend User model structure.
 */
export interface User {
  id: number;                                                    // Unique user identifier
  email: string;                                                 // User's email address (used for login)
  first_name: string;                                            // User's first name
  last_name: string;                                             // User's last name
  role: 'admin' | 'editor' | 'approver' | 'viewer';            // User's role (determines permissions)
  business: number;                                              // ID of associated business
  business_name: string;                                         // Name of associated business (for display)
  password_change_required?: boolean;                            // Whether user must change password (for invitations)
}

/**
 * Authentication Response Interface
 * 
 * Represents the response structure from login and registration endpoints.
 * Contains user data and JWT tokens for authentication.
 */
export interface AuthResponse {
  user: User;                                                    // User profile data
  tokens: {
    access: string;                                              // Short-lived access token (1 hour)
    refresh: string;                                             // Long-lived refresh token (7 days)
  };
}

/**
 * User Login Function
 * 
 * Authenticates a user with email and password, stores tokens and user data
 * in localStorage for session persistence.
 * 
 * Process:
 * 1. Send login request to backend
 * 2. Extract tokens and user data from response
 * 3. Store tokens in localStorage for API requests
 * 4. Store user data for immediate access
 * 5. Return complete auth response
 * 
 * @param email - User's email address
 * @param password - User's password (could be temporary password)
 * @returns Promise<AuthResponse> - User data and tokens
 * 
 * Usage:
 * ```typescript
 * const { user, tokens } = await login('user@example.com', 'password');
 * ```
 */
export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post('/auth/login/', { email, password });
  const { tokens, user } = response.data;
  
  // Store authentication tokens for API requests
  localStorage.setItem('access_token', tokens.access);
  localStorage.setItem('refresh_token', tokens.refresh);
  
  // Store user data for immediate access without API calls
  localStorage.setItem('user', JSON.stringify(user));
  
  return response.data;
};

/**
 * User Registration Function
 * 
 * Registers a new user and creates their associated business. This is used
 * when business owners first sign up for the platform.
 * 
 * Process:
 * 1. Send registration request with user and business data
 * 2. Backend creates user account and associated business
 * 3. Store returned tokens and user data
 * 4. User is immediately logged in after registration
 * 
 * @param data - Registration data including user and business information
 * @returns Promise<AuthResponse> - User data and tokens
 * 
 * Business Logic:
 * - Creates both user account and business in one operation
 * - User becomes the owner/admin of the created business
 * - Automatic login after successful registration
 */
export const register = async (data: {
  email: string;                                                 // User's email address
  password: string;                                              // User's chosen password
  first_name: string;                                            // User's first name
  last_name: string;                                             // User's last name
  business_name: string;                                         // Name of business to create
}): Promise<AuthResponse> => {
  const response = await api.post('/auth/register/', data);
  const { tokens, user } = response.data;
  
  // Store authentication data (same as login)
  localStorage.setItem('access_token', tokens.access);
  localStorage.setItem('refresh_token', tokens.refresh);
  localStorage.setItem('user', JSON.stringify(user));
  
  return response.data;
};

/**
 * User Logout Function
 * 
 * Clears all authentication data from localStorage, effectively logging
 * the user out of the application.
 * 
 * Security:
 * - Removes all stored tokens
 * - Clears user data
 * - Forces re-authentication for future requests
 * 
 * Note: This is a client-side logout. For enhanced security, consider
 * implementing server-side token invalidation.
 */
export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

/**
 * Get Current User Function
 * 
 * Retrieves the currently authenticated user from localStorage.
 * Used for session restoration and user state management.
 * 
 * SSR Compatibility:
 * - Returns null during server-side rendering (no window object)
 * - Safe to use in Next.js components
 * 
 * @returns User | null - Current user data or null if not authenticated
 * 
 * Usage:
 * ```typescript
 * const user = getCurrentUser();
 * if (user) {
 *   console.log(`Welcome ${user.first_name}!`);
 * }
 * ```
 */
export const getCurrentUser = (): User | null => {
  // SSR safety check - localStorage only available in browser
  if (typeof window === 'undefined') return null;
  
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

/**
 * Authentication Status Check Function
 * 
 * Checks if a user is currently authenticated by verifying the presence
 * of an access token in localStorage.
 * 
 * SSR Compatibility:
 * - Returns false during server-side rendering
 * - Safe for use in Next.js components and middleware
 * 
 * @returns boolean - True if user is authenticated, false otherwise
 * 
 * Usage:
 * ```typescript
 * if (isAuthenticated()) {
 *   // User is logged in
 *   showDashboard();
 * } else {
 *   // User needs to log in
 *   showLoginForm();
 * }
 * ```
 * 
 * Note: This only checks for token presence, not validity.
 * Token validation happens automatically in the API client.
 */
export const isAuthenticated = (): boolean => {
  // SSR safety check - localStorage only available in browser
  if (typeof window === 'undefined') return false;
  
  return !!localStorage.getItem('access_token');
};
