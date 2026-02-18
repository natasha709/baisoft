'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';
import { Building2, Save, AlertCircle, Users, LayoutDashboard, MessageSquare } from 'lucide-react';

interface BusinessData {
    id: number;
    name: string;
    description: string;
}

export default function BusinessSettings() {
    const { user, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const [business, setBusiness] = useState<BusinessData | null>(null);
    const [formData, setFormData] = useState({ name: '', description: '' });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        if (!user) {
            router.push('/login');
            return;
        }
        fetchBusiness();
    }, [user, router]);

    const fetchBusiness = async () => {
        try {
            const response = await api.get('/auth/businesses/');
            // ViewSet returns array even for single result due to filter
            const data = response.data.results || response.data;
            const b = Array.isArray(data) ? data[0] : data;
            if (b) {
                setBusiness(b);
                setFormData({ name: b.name, description: b.description || '' });
            }
        } catch (err) {
            console.error('Error fetching business:', err);
            setError('Failed to load business details');
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!business) return;

        setSaving(true);
        setError('');
        setSuccess('');

        try {
            await api.patch(`/auth/businesses/${business.id}/`, formData);
            setSuccess('Business settings updated successfully');
            fetchBusiness();
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to update business settings');
        } finally {
            setSaving(false);
        }
    };

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    if (!user) return null;

    return (
        <div className="flex h-screen bg-gray-50">
            {/* Sidebar */}
            <div className="w-64 bg-[#001529] text-white shadow-lg flex flex-col transition-colors duration-200">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-white">Product Marketplace</h1>
                </div>

                <nav className="mt-6 flex-1 space-y-1">
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

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                <div className="p-8 max-w-4xl">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Business Settings</h2>

                    {loading ? (
                        <div className="text-center py-12">
                            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        </div>
                    ) : (
                        <div className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-100">
                            <div className="p-6 sm:p-8">
                                <form onSubmit={handleSubmit} className="space-y-6">
                                    {error && (
                                        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg flex items-center gap-3">
                                            <AlertCircle className="w-5 h-5" />
                                            {error}
                                        </div>
                                    )}

                                    {success && (
                                        <div className="bg-green-50 border border-green-200 text-green-700 p-4 rounded-lg flex items-center gap-3">
                                            <div className="bg-green-100 rounded-full p-1">
                                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                                </svg>
                                            </div>
                                            {success}
                                        </div>
                                    )}

                                    <div className="space-y-2">
                                        <label className="block text-sm font-medium text-gray-700">
                                            Business Name
                                        </label>
                                        <input
                                            type="text"
                                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all shadow-sm"
                                            value={formData.name}
                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                            placeholder="Enter business name"
                                            required
                                        />
                                    </div>

                                    <div className="space-y-2">
                                        <label className="block text-sm font-medium text-gray-700">
                                            Description
                                        </label>
                                        <textarea
                                            rows={5}
                                            className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all shadow-sm resize-none"
                                            value={formData.description}
                                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                            placeholder="Tell us about your business..."
                                        />
                                    </div>

                                    <div className="pt-4 flex justify-end">
                                        <button
                                            type="submit"
                                            disabled={saving}
                                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all disabled:opacity-70"
                                        >
                                            {saving ? (
                                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                            ) : (
                                                <Save className="w-5 h-5" />
                                            )}
                                            {saving ? 'Saving changes...' : 'Save Settings'}
                                        </button>
                                    </div>
                                </form>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
