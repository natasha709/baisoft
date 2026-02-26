/**
 * Authentication Context for Product Marketplace
 * =============================================
 * 
 * This module provides global authentication state management using React Context.
 * It handles user authentication, permissions, and provides auth-related utilities
 * throughout the application.
 * 
 * Key Features:
 * - Global user state management
 * - Role-based permission checking
 * - Automatic user session restoration
 * - Logout functionality with cleanup
 * - TypeScript support for type safety
 * 
 * Permission System:
 * - Admin: Full access (create, edit, approve, delete, view)
 * - Editor: Create and edit products, view all
 * - Approver: Approve products, view all
 * - Viewer: View all products only
 * 
 * Usage:
 * - Wrap app with AuthProvider in layout
 * - Use useAuth hook in components to access auth state
 * - Check permissions with hasPermission method
 */

'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, getCurrentUser, logout as authLogout } from '@/lib/auth';

/**
 * Authentication Context Type Definition
 * 
 * Defines the shape of the authentication context that components can access.
 * Provides user state, setters, and utility functions.
 */
interface AuthContextType {
  user: User | null;                              // Current authenticated user or null
  setUser: (user: User | null) => void;           // Function to update user state
  logout: () => void;                             // Function to logout user
  hasPermission: (permission: string) => boolean; // Function to check user permissions
}

// Create the authentication context with undefined default
// This forces components to use the context within a provider
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Authentication Provider Component
 * 
 * This component wraps the entire application and provides authentication
 * state to all child components. It handles user session restoration and
 * provides authentication utilities.
 * 
 * Features:
 * - Restores user session on app load
 * - Provides user state to all components
 * - Handles logout with proper cleanup
 * - Implements role-based permission checking
 * 
 * @param children - Child components that need access to auth context
 */
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // User state - null means not authenticated, User object means authenticated
  const [user, setUser] = useState<User | null>(null);

  /**
   * Effect: Restore User Session on App Load
   * 
   * When the app loads, check if there's a valid user session
   * and restore the user state. This allows users to stay logged in
   * across browser sessions.
   */
  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
  }, []);

  /**
   * Logout Function
   * 
   * Handles complete user logout process:
   * 1. Call auth logout to clear tokens
   * 2. Clear user state in context
   * 3. Redirect to landing page
   * 
   * This ensures complete cleanup of authentication state.
   */
  const logout = () => {
    // Clear tokens and auth state
    authLogout();
    
    // Clear user from context
    setUser(null);

    // Always redirect to landing page after logout
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  };

  /**
   * Permission Checking Function
   * 
   * Implements role-based access control by checking if the current user
   * has a specific permission based on their role.
   * 
   * Permission Matrix:
   * - admin: All permissions (full system access)
   * - editor: create_product, edit_product, view_all
   * - approver: approve_product, view_all
   * - viewer: view_all only
   * 
   * @param permission - The permission to check (e.g., 'create_product')
   * @returns boolean - True if user has permission, false otherwise
   */
  const hasPermission = (permission: string): boolean => {
    // No user means no permissions
    if (!user) return false;
    
    // Define permission matrix for each role
    const permissions: Record<string, string[]> = {
      admin: ['create_product', 'edit_product', 'approve_product', 'delete_product', 'view_all'],
      editor: ['create_product', 'edit_product', 'view_all'],
      approver: ['approve_product', 'view_all'],
      viewer: ['view_all'],
    };
    
    // Check if user's role includes the requested permission
    return permissions[user.role]?.includes(permission) || false;
  };

  // Provide authentication context to all child components
  return (
    <AuthContext.Provider value={{ user, setUser, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

/**
 * useAuth Hook
 * 
 * Custom hook that provides easy access to authentication context.
 * This hook must be used within components wrapped by AuthProvider.
 * 
 * @returns AuthContextType - Authentication context with user state and utilities
 * @throws Error if used outside of AuthProvider
 * 
 * Usage Example:
 * ```tsx
 * const { user, hasPermission, logout } = useAuth();
 * 
 * if (!user) {
 *   return <LoginForm />;
 * }
 * 
 * if (hasPermission('create_product')) {
 *   return <CreateProductButton />;
 * }
 * ```
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  
  // Ensure hook is used within AuthProvider
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};
