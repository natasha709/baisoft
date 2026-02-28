'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';
import { Building2, Users, LayoutDashboard, MessageSquare, TrendingUp } from 'lucide-react';

interface Product {
  id: number;
  name: string;
  description: string;
  price: string;
  status: 'draft' | 'pending_approval' | 'approved';
  created_by_email: string;
  business: number;
  business_name: string;
}

interface Business {
  id: number;
  name: string;
}

export default function Dashboard() {

  const { user, logout, hasPermission } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const [products, setProducts] = useState<Product[]>([]);
  const [businesses, setBusinesses] = useState<Business[]>([]);
  const [loading, setLoading] = useState(true);

  const [showCreateForm, setShowCreateForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    business: ''
  });
  const [error, setError] = useState('');

  const [editing, setEditing] = useState<Product | null>(null);
  const [editData, setEditData] = useState({
    name: '',
    description: '',
    price: '',
    business: ''
  });
  const [editError, setEditError] = useState('');
  const [editSaving, setEditSaving] = useState(false);

  const [viewing, setViewing] = useState<Product | null>(null);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingProduct, setDeletingProduct] = useState<{
    id: number;
    name: string;
  } | null>(null);

  useEffect(() => {

    if (!user) {
      router.push('/login');
      return;
    }

    fetchProducts();
    fetchBusinesses();
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

  const fetchBusinesses = async () => {
    try {
      const response = await api.get('/auth/businesses/');
      const data = response.data.results || response.data;
      setBusinesses(data);

      if (data.length > 0) {

        const defaultBusiness = data.find((b: any) => b.id === user?.business) || data[0];
        setFormData(prev => ({ ...prev, business: defaultBusiness.id.toString() }));
      }
    } catch (err) {
      console.error('Error fetching businesses:', err);

    }
  };

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await api.post('/products/', formData);

      setFormData({
        name: '',
        description: '',
        price: '',
        business: businesses[0]?.id.toString() || ''
      });
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

  const handleDelete = async (id: number, name: string) => {

    setDeletingProduct({ id, name });
    setShowDeleteModal(true);
  };

  const confirmDeleteProduct = async () => {
    if (!deletingProduct) return;

    try {
      await api.delete(`/products/${deletingProduct.id}/`);

      setShowDeleteModal(false);
      setDeletingProduct(null);

      fetchProducts();
    } catch (err: any) {

      alert(err.response?.data?.error || 'Failed to delete product');
      setShowDeleteModal(false);
      setDeletingProduct(null);
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

  const openEdit = (p: Product) => {
    setEditError('');

    setEditing(p);
    setEditData({
      name: p.name,
      description: p.description,
      price: p.price,
      business: p.business.toString()
    });
  };

  const closeEdit = () => {
    setEditing(null);
    setEditError('');
    setEditSaving(false);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editing) return;

    setEditError('');
    setEditSaving(true);

    try {
      await api.patch(`/products/${editing.id}/`, editData);
      closeEdit();
      fetchProducts();
    } catch (err: any) {

      setEditError(err.response?.data?.detail || err.response?.data?.error || 'Failed to update product');
      setEditSaving(false);
    }
  };

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
      {}
      <div className="w-64 bg-[#001529] text-white shadow-lg flex flex-col transition-colors duration-200">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-white">Product Marketplace</h1>
        </div>

        <nav className="mt-6 flex-1 space-y-1">
          {user.role === 'admin' && (
            <Link
              href="/admin/dashboard"
              className={`flex items-center px-6 py-3 transition-colors ${pathname === '/admin/dashboard'
                ? 'text-white bg-blue-600 border-r-4 border-blue-400'
                : 'text-gray-300 hover:bg-[#002140] hover:text-white'
                }`}
            >
              <TrendingUp className="w-5 h-5 mr-3" />
              Admin Dashboard
            </Link>
          )}

          {user.role === 'admin' && (
            <Link
              href="/users"
              className={`flex items-center px-6 py-3 transition-colors ${pathname === '/users'
                ? 'text-white bg-blue-600 border-r-4 border-blue-400'
                : 'text-gray-300 hover:bg-[#002140] hover:text-white'
                }`}
            >
              <Users className="w-5 h-5 mr-3" />
              Manage Users
            </Link>
          )}

          <Link
            href="/dashboard"
            className={`flex items-center px-6 py-3 transition-colors ${pathname === '/dashboard'
              ? 'text-white bg-blue-600 border-r-4 border-blue-400'
              : 'text-gray-300 hover:bg-[#002140] hover:text-white'
              }`}
          >
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Products
          </Link>

          <Link
            href="/business"
            className={`flex items-center px-6 py-3 transition-colors ${pathname === '/business'
              ? 'text-white bg-blue-600 border-r-4 border-blue-400'
              : 'text-gray-300 hover:bg-[#002140] hover:text-white'
              }`}
          >
            <Building2 className="w-5 h-5 mr-3" />
            Business
          </Link>

          <Link
            href="/chatbot"
            className={`flex items-center px-6 py-3 transition-colors ${pathname === '/chatbot'
              ? 'text-white bg-blue-600 border-r-4 border-blue-400'
              : 'text-gray-300 hover:bg-[#002140] hover:text-white'
              }`}
          >
            <MessageSquare className="w-5 h-5 mr-3" />
            AI Chatbot
          </Link>
        </nav>

        <div className="border-t border-gray-700">
          <div className="p-4 bg-[#001529]">
            <p className="text-sm font-medium text-white">{user.business_name}</p>
            <p className="text-xs text-gray-400 mt-1">{user.email}</p>
            <p className="text-xs text-gray-500">{user.role}</p>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-6 py-3 text-white hover:bg-red-900/20 transition-colors"
          >
            <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            Logout
          </button>
        </div>
      </div>

      {}
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

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <p className="text-gray-500">No products yet. Create your first product!</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-[#001529]">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Product
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Business
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Created By
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-white uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {products.map((product) => (
                    <tr key={product.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{product.name}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-700 line-clamp-2">{product.description}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-blue-600">${product.price}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(product.status)}`}
                        >
                          {product.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900 font-medium">{product.business_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">{product.created_by_email}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                        <button
                          onClick={() => setViewing(product)}
                          className="inline-flex items-center justify-center text-gray-600 hover:text-gray-800"
                          aria-label="View product"
                          title="View product"
                        >
                          <svg
                            className="w-4 h-4"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                            aria-hidden="true"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                            />
                          </svg>
                        </button>
                        {hasPermission('edit_product') && (
                          <button
                            onClick={() => openEdit(product)}
                            className="inline-flex items-center justify-center text-blue-600 hover:text-blue-800"
                            aria-label="Edit product"
                            title="Edit product"
                          >
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                              aria-hidden="true"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15.232 5.232a2.5 2.5 0 013.536 3.536L8.5 19.036 4 20l.964-4.5 10.268-10.268z"
                              />
                            </svg>
                          </button>
                        )}
                        {product.status === 'draft' && hasPermission('edit_product') && (
                          <button
                            onClick={() => handleSubmitForApproval(product.id)}
                            className="inline-flex items-center px-3 py-1 rounded bg-yellow-600 text-white hover:bg-yellow-700"
                          >
                            Submit
                          </button>
                        )}
                        {product.status === 'pending_approval' && hasPermission('approve_product') && (
                          <button
                            onClick={() => handleApprove(product.id)}
                            className="inline-flex items-center px-3 py-1 rounded bg-green-600 text-white hover:bg-green-700"
                          >
                            Approve
                          </button>
                        )}
                        {hasPermission('delete_product') && (
                          <button
                            onClick={() => handleDelete(product.id, product.name)}
                            className="inline-flex items-center justify-center w-8 h-8 rounded-full text-red-600 hover:text-red-800 hover:bg-red-50"
                            aria-label="Delete product"
                            title="Delete product"
                          >
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                              aria-hidden="true"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5-3h4m-4 0H9m6 0h1m-9 3h10M10 11v6m4-6v6"
                              />
                            </svg>
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-lg rounded-lg shadow-xl">
            <div className="px-6 py-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Create New Product</h3>
              <button
                onClick={() => setShowCreateForm(false)}
                className="text-gray-500 hover:text-gray-800"
                aria-label="Close create product"
              >
                x
              </button>
            </div>
            <form onSubmit={handleCreateProduct} className="p-6 space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded p-3">
                  {error}
                </div>
              )}
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
                className="w-full max-w-md mx-auto px-3 py-2 border border-gray-300 rounded"
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
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Business</label>
                <select
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded bg-white"
                  value={formData.business}
                  onChange={(e) => setFormData({ ...formData, business: e.target.value })}
                >
                  <option value="" disabled>Select a business</option>
                  {businesses.map(b => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 rounded border border-gray-300 text-gray-700 hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {}
      {editing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-lg rounded-lg shadow-xl">
            <div className="px-6 py-4 border-b flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Edit Product</h3>
              <button
                onClick={closeEdit}
                className="text-gray-500 hover:text-gray-800"
                aria-label="Close"
              >
                x
              </button>
            </div>
            <form onSubmit={handleSaveEdit} className="p-6 space-y-4">
              {editError && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded p-3">
                  {editError}
                </div>
              )}
              <input
                type="text"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded"
                value={editData.name}
                onChange={(e) => setEditData({ ...editData, name: e.target.value })}
                placeholder="Product name"
              />
              <textarea
                required
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded"
                value={editData.description}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                placeholder="Description"
              />
              <input
                type="number"
                step="0.01"
                required
                className="w-full px-3 py-2 border border-gray-300 rounded"
                value={editData.price}
                onChange={(e) => setEditData({ ...editData, price: e.target.value })}
                placeholder="Price"
              />
              <div className="space-y-1">
                <label className="text-sm font-medium text-gray-700">Business</label>
                <select
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded bg-white"
                  value={editData.business}
                  onChange={(e) => setEditData({ ...editData, business: e.target.value })}
                >
                  <option value="" disabled>Select a business</option>
                  {businesses.map(b => (
                    <option key={b.id} value={b.id}>
                      {b.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={closeEdit}
                  className="px-4 py-2 rounded border border-gray-300 text-gray-700 hover:bg-gray-100"
                  disabled={editSaving}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50"
                  disabled={editSaving}
                >
                  {editSaving ? 'Saving…' : 'Save changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {}
      {viewing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
          <div className="bg-white w-full max-w-2xl rounded-lg shadow-xl">
            <div className="px-6 py-4 border-b flex items-center justify-between bg-[#001529]">
              <h3 className="text-lg font-semibold text-white">Product Details</h3>
              <button
                onClick={() => setViewing(null)}
                className="text-white hover:text-gray-300"
                aria-label="Close"
              >
                x
              </button>
            </div>
            <div className="p-6 space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Product Name</label>
                  <p className="text-lg font-semibold text-gray-900">{viewing.name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Price</label>
                  <p className="text-lg font-semibold text-blue-600">${viewing.price}</p>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">Description</label>
                <p className="text-gray-700 leading-relaxed">{viewing.description}</p>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Status</label>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(viewing.status)}`}
                  >
                    {viewing.status.replace('_', ' ')}
                  </span>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Business</label>
                  <p className="text-gray-900 font-medium">{viewing.business_name}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-500 mb-1">Created By</label>
                  <p className="text-gray-700">{viewing.created_by_email}</p>
                </div>
              </div>

              <div className="pt-4 border-t flex justify-end">
                <button
                  onClick={() => setViewing(null)}
                  className="px-6 py-2 rounded bg-gray-100 text-gray-700 hover:bg-gray-200 font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4">
          <div className="bg-white w-full max-w-md rounded-lg shadow-xl">
            <div className="p-6">
              <div className="flex items-center justify-center w-12 h-12 mx-auto bg-red-100 rounded-full mb-4">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 text-center mb-2">Delete Product</h3>
              <p className="text-gray-600 text-center mb-6">
                Are you sure you want to delete product <span className="font-medium">{deletingProduct?.name}</span>? This action cannot be undone.
              </p>
              <div className="flex justify-end gap-2">
                <button
                  onClick={() => {
                    setShowDeleteModal(false);
                    setDeletingProduct(null);
                  }}
                  className="px-4 py-2 rounded border border-gray-300 text-gray-700 hover:bg-gray-100"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmDeleteProduct}
                  className="px-4 py-2 rounded bg-red-600 text-white hover:bg-red-700"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
