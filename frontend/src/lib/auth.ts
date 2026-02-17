import api from './api';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'editor' | 'approver' | 'viewer';
  business: number;
  business_name: string;
  password_change_required?: boolean;
}

export interface AuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
}

export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await api.post('/auth/login/', { email, password });
  const { tokens, user } = response.data;
  
  localStorage.setItem('access_token', tokens.access);
  localStorage.setItem('refresh_token', tokens.refresh);
  localStorage.setItem('user', JSON.stringify(user));
  
  return response.data;
};

export const register = async (data: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  business_name: string;
}): Promise<AuthResponse> => {
  const response = await api.post('/auth/register/', data);
  const { tokens, user } = response.data;
  
  localStorage.setItem('access_token', tokens.access);
  localStorage.setItem('refresh_token', tokens.refresh);
  localStorage.setItem('user', JSON.stringify(user));
  
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
};

export const getCurrentUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem('user');
  return userStr ? JSON.parse(userStr) : null;
};

export const isAuthenticated = (): boolean => {
  if (typeof window === 'undefined') return false;
  return !!localStorage.getItem('access_token');
};
