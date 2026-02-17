'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';

interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  status: 'draft' | 'pending_approval' | 'approved';
  created_by_email: string;
}

export default function Dashboard() {
  const { user, logout, hasPermission } = useAuth();
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({ name: '', description: '', price: '' });
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    fetchProducts();
  }, [user, router]);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/');
      setProducts(response.data.results || response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      await api.post('/products/', formData);
      setFormData({ name: '', description: '', price: '' });
      setShowCreateForm(false);
      fetchProducts();
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to create product');
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await api.post(`/products/${id}/approve/`);
      fetchProducts();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to approve product');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
      await api.delete(`/products/${id}/`);
      fetchProducts();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to delete product');
    }
  };

  const handleSubmitForApproval = async (id: number) => {
    try {
      await api.post(`/products/${id}/submit_for_approval/`);
      fetchProducts();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to submit for approval');
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  if (!user) return null;

  const getStatusBadge = (status: string) => {
    const colors = {
      draft: 'bg-gray-200 text-gray-800',
      pending_approval: 'bg-yellow-200 text-yellow-800',
      approved: 'bg-green-200 text-green-800',
    };
    return colors[status as keyof typeof colors] || 'bg-gray-200 text-gray-800';
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-lg flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-gray-900">Product Marketplace</h1>
        </div>
        
        <nav className="mt-6 flex-1">
          <Link 
            href="/dashboard" 
            className="flex items-center px-6 py-3 text-blue-600 bg-blue-50 border-r-4 border-blue-600"
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
            </svg>
            Products
          </Link>
          
          {user.role === 'admin' && (
            <Link 
              href="/users" 
              className="flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100 hover:text-blue-600"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
              Manage Users
            </Link>
          )}
          
          <Link 
            href="/chatbot" 
            className="flex items-center px-6 py-3 text-gray-700 hover:bg-gray-100 hover:text-blue-600"
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            </svg>
            AI Chatbot
          </Link>
        </nav>
        
        <div className="border-t border-gray-200">
          <div className="p-4 bg-gray-50">
            <p className="text-sm font-medium text-gray-900">{user.business_name}</p>
            <p className="text-xs text-gray-600 mt-1">{user.email}</p>
            <p className="text-xs text-gray-500">{user.role}</p>
          </div>
          <button 
            onClick={handleLogout}
            className="flex items-center w-full px-6 py-3 text-red-600 hover:bg-red-50"
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Products</h2>
            {hasPermission('create_product') && (
              <button
                onClick={() => setShowCreateForm(!showCreateForm)}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                {showCreateForm ? 'Cancel' : 'Create Product'}
              </button>
            )}
          </div>

        {showCreateForm && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4">Create New Product</h3>
            {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4">{error}</div>}
            <form onSubmit={handleCreateProduct} className="space-y-4">
              <input
                type="text"
                placeholder="Product Name"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
              <textarea
                placeholder="Description"
                required
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
              <input
                type="number"
                step="0.01"
                placeholder="Price"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              />
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
              >
                Create
              </button>
            </form>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : products.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg shadow">
            <p className="text-gray-500">No products yet. Create your first product!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {products.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold">{product.name}</h3>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(product.status)}`}>
                        {product.status.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-gray-600 mb-2">{product.description}</p>
                    <p className="text-2xl font-bold text-blue-600">${product.price}</p>
                    <p className="text-sm text-gray-500 mt-2">Created by: {product.created_by_email}</p>
                  </div>
                  <div className="flex flex-col gap-2">
                    {product.status === 'draft' && hasPermission('edit_product') && (
                      <button
                        onClick={() => handleSubmitForApproval(product.id)}
                        className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700 text-sm"
                      >
                        Submit for Approval
                      </button>
                    )}
                    {product.status === 'pending_approval' && hasPermission('approve_product') && (
                      <button
                        onClick={() => handleApprove(product.id)}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm"
                      >
                        Approve
                      </button>
                    )}
                    {hasPermission('delete_product') && (
                      <button
                        onClick={() => handleDelete(product.id)}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 text-sm"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
