'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';
import {
    LayoutDashboard,
    Building2,
    Users,
    MessageSquare,
    ShoppingCart,
    Clock,
    CheckCircle2,
    AlertCircle,
    TrendingUp,
    Package
} from 'lucide-react';

interface Stats {
    total_products: number;
    pending_approval: number;
    approved_products: number;
    total_businesses: number;
    total_users: number;
}

export default function AdminDashboard() {
    const { user, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    const [stats, setStats] = useState<Stats>({
        total_products: 0,
        pending_approval: 0,
        approved_products: 0,
        total_businesses: 0,
        total_users: 0
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!user) {
            router.push('/login');
            return;
        }
        if (user.role !== 'admin') {
            router.push('/dashboard');
            return;
        }
        fetchStats();
    }, [user, router]);

    const fetchStats = async () => {
        try {
            // Ideally we'd have a specific analytics endpoint, but for now we aggregate
            const [productsRes, businessesRes, usersRes] = await Promise.all([
                api.get('/products/'),
                api.get('/auth/businesses/'),
                api.get('/auth/users/')
            ]);

            const products = productsRes.data.results || productsRes.data;
            const businesses = businessesRes.data.results || businessesRes.data;
            const users = usersRes.data.results || usersRes.data;

            setStats({
                total_products: products.length,
                pending_approval: products.filter((p: any) => p.status === 'pending_approval').length,
                approved_products: products.filter((p: any) => p.status === 'approved').length,
                total_businesses: businesses.length,
                total_users: users.length
            });
        } catch (error) {
            console.error('Error fetching admin stats:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
        router.push('/');
    };

    if (!user || user.role !== 'admin') return null;

    const statCards = [
        {
            title: 'Total Products',
            value: stats.total_products,
            description: 'Managed items across all companies',
            icon: Package,
            color: 'bg-blue-600',
            trend: '+12%'
        },
        {
            title: 'Pending Approval',
            value: stats.pending_approval,
            description: 'Requires immediate attention',
            icon: Clock,
            color: 'bg-amber-500',
            trend: stats.pending_approval > 5 ? 'High' : 'Low'
        },
        {
            title: 'Approved Catalog',
            value: stats.approved_products,
            description: 'Published and live products',
            icon: CheckCircle2,
            color: 'bg-emerald-600',
            trend: 'Stable'
        },
        {
            title: 'Registered Companies',
            value: stats.total_businesses,
            description: 'Active business entities',
            icon: Building2,
            color: 'bg-purple-600',
            trend: '+2 new'
        }
    ];

    return (
        <div className="flex h-screen bg-[#F8FAFC]">
            {/* Sidebar */}
            <div className="w-64 bg-[#001529] text-white shadow-lg flex flex-col transition-colors duration-200">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-white">Product Marketplace</h1>
                </div>

                <nav className="mt-6 flex-1 space-y-1">
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
                        href="/users"
                        className={`flex items-center px-6 py-3 transition-colors ${pathname === '/users'
                            ? 'text-white bg-blue-600 border-r-4 border-blue-400'
                            : 'text-gray-300 hover:bg-[#002140] hover:text-white'
                            }`}
                    >
                        <Users className="w-5 h-5 mr-3" />
                        Manage Users
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
                        <p className="text-sm font-medium text-white">{user.business_name || 'System Admin'}</p>
                        <p className="text-xs text-gray-400 mt-1">{user.email}</p>
                        <p className="text-xs text-gray-500 uppercase font-black tracking-tighter">{user.role}</p>
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
                <div className="p-8 max-w-7xl">
                    <div className="mb-10">
                        <h2 className="text-4xl font-black text-gray-900 tracking-tight">System Overview</h2>
                        <p className="text-gray-500 mt-2 text-lg">Performance and operational metrics for the entire marketplace.</p>
                    </div>

                    {loading ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-pulse">
                            {[1, 2, 3, 4].map((i) => (
                                <div key={i} className="h-40 bg-white rounded-3xl border border-gray-100 shadow-sm"></div>
                            ))}
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                            {statCards.map((card, idx) => (
                                <div
                                    key={idx}
                                    className="bg-white p-8 rounded-[2rem] shadow-xl shadow-gray-200/50 border border-gray-100 group hover:border-blue-500 hover:shadow-blue-500/10 transition-all duration-300"
                                >
                                    <div className="flex items-start justify-between mb-6">
                                        <div className={`p-4 rounded-2xl ${card.color} text-white shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                                            <card.icon className="w-8 h-8" />
                                        </div>
                                        <span className={`text-xs font-black uppercase px-2.5 py-1 rounded-full ${card.trend.includes('+') ? 'bg-emerald-100 text-emerald-600' : 'bg-gray-100 text-gray-400'
                                            }`}>
                                            {card.trend}
                                        </span>
                                    </div>
                                    <h3 className="text-gray-500 font-bold text-sm uppercase tracking-widest mb-1">{card.title}</h3>
                                    <div className="flex items-baseline gap-2">
                                        <span className="text-5xl font-black text-gray-900 tracking-tighter">
                                            {card.value}
                                        </span>
                                    </div>
                                    <p className="text-gray-400 text-sm mt-4 font-medium leading-relaxed">
                                        {card.description}
                                    </p>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Quick Actions or Recent Activity Section */}
                    <div className="mt-12 grid grid-cols-1 lg:grid-cols-3 gap-8">
                        <div className="lg:col-span-2 bg-white rounded-[2rem] p-8 border border-gray-100 shadow-xl shadow-gray-200/50">
                            <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                                <TrendingUp className="text-blue-600 w-6 h-6" />
                                Marketplace Pulse
                            </h3>
                            <div className="h-64 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 flex items-center justify-center text-gray-400 font-medium">
                                Growth data visualization coming soon
                            </div>
                        </div>

                        <div className="bg-[#001529] rounded-[2rem] p-8 text-white shadow-2xl">
                            <h3 className="text-2xl font-bold mb-6">Quick Links</h3>
                            <div className="space-y-4">
                                <Link
                                    href="/users"
                                    className="block p-4 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all group"
                                >
                                    <div className="font-bold text-gray-200 group-hover:text-white">Review Users</div>
                                    <div className="text-xs text-gray-400 mt-1">Audit and manage active accounts</div>
                                </Link>
                                <Link
                                    href="/dashboard"
                                    className="block p-4 bg-white/5 hover:bg-white/10 rounded-2xl border border-white/10 transition-all group"
                                >
                                    <div className="font-bold text-gray-200 group-hover:text-white">Audit Catalog</div>
                                    <div className="text-xs text-gray-400 mt-1">Approve or reject pending products</div>
                                </Link>
                                <button
                                    onClick={() => alert('Launching site audit...')}
                                    className="w-full mt-4 p-4 bg-blue-600 hover:bg-blue-700 rounded-2xl font-black uppercase text-sm tracking-widest transition-all shadow-lg shadow-blue-600/30 active:scale-95"
                                >
                                    Generate Report
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
