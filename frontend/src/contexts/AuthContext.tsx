'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, getCurrentUser, logout as authLogout } from '@/lib/auth';

interface AuthContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const currentUser = getCurrentUser();
    setUser(currentUser);
  }, []);

  const logout = () => {
    authLogout();
    setUser(null);
  };

  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    
    const permissions: Record<string, string[]> = {
      admin: ['create_product', 'edit_product', 'approve_product', 'delete_product', 'view_all'],
      editor: ['create_product', 'edit_product', 'view_all'],
      approver: ['approve_product', 'view_all'],
      viewer: ['view_all'],
    };
    
    return permissions[user.role]?.includes(permission) || false;
  };

  return (
    <AuthContext.Provider value={{ user, setUser, logout, hasPermission }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
