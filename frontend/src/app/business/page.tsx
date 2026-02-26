/**
 * Business Management Page Component - Multi-Tenant Business Administration
 * ========================================================================
 * 
 * This component provides a comprehensive business management interface for
 * administrators to manage their organizations, configure settings, and
 * oversee team members within a multi-tenant SaaS environment.
 * 
 * Key Features:
 * - Multi-business management (view and switch between businesses)
 * - Business settings configuration (name, capabilities)
 * - Team member management (invite, edit, remove users)
 * - Role-based access control with granular permissions
 * - Business capability toggles (user creation, role assignment)
 * - Modal-based forms for creating businesses and managing users
 * - Professional enterprise-grade UI with modern design
 * 
 * Business Management Capabilities:
 * - View all managed businesses in card-based layout
 * - Create new businesses with initial team member
 * - Configure business settings and capabilities
 * - Toggle user creation permissions
 * - Toggle role assignment permissions
 * - Switch between different businesses seamlessly
 * 
 * Team Management Features:
 * - View all team members in professional table layout
 * - Invite new team members with role assignment
 * - Edit existing team member roles and information
 * - Remove team members with confirmation
 * - Role-based UI (only show actions based on permissions)
 * - Visual role indicators with color coding
 * 
 * Access Control & Security:
 * - Authentication guard (redirects to login if not authenticated)
 * - Business isolation (users only see their business data)
 * - Permission-based UI rendering
 * - Capability-based feature access
 * - Secure API calls with proper error handling
 * 
 * User Interface Design:
 * - Three-tab navigation (Companies, Settings, Team)
 * - Responsive design with mobile-friendly layout
 * - Professional sidebar navigation
 * - Modal-based forms with validation
 * - Loading states and error handling
 * - Success/error notifications
 * - Modern card-based layouts
 * 
 * Business Roles & Permissions:
 * - Admin: Full access to all business settings and user management
 * - Editor: Can create and edit products (limited business access)
 * - Approver: Can approve products only (limited business access)
 * - Viewer: Read-only access (limited business access)
 * 
 * Multi-Tenancy Support:
 * - Business isolation ensures data security
 * - Users can only access their assigned business
 * - Business-specific team member management
 * - Capability-based feature toggles per business
 * 
 * Technical Implementation:
 * - React hooks for state management
 * - Next.js App Router with client-side navigation
 * - TypeScript interfaces for type safety
 * - Tailwind CSS for responsive styling
 * - Lucide React icons for consistent iconography
 * - Custom authentication context integration
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';
import Link from 'next/link';
import {
    Building2, Save, AlertCircle, Users, LayoutDashboard,
    MessageSquare, UserPlus, Shield, Mail, Edit, Trash2,
    CheckCircle2, XCircle, TrendingUp
} from 'lucide-react';

/**
 * TypeScript Interface Definitions
 * ================================
 * 
 * BusinessData: Represents a business entity with configuration settings
 * - id: Unique business identifier
 * - name: Legal business name
 * - can_create_users: Permission to invite new team members
 * - can_assign_roles: Permission to modify user roles
 * 
 * User: Represents a team member within a business
 * - id: Unique user identifier
 * - email: User's email address (used for authentication)
 * - first_name: User's first name
 * - last_name: User's last name
 * - role: User's role (admin, editor, approver, viewer)
 */
interface BusinessData {
    id: number;
    name: string;
    can_create_users: boolean;
    can_assign_roles: boolean;
}

interface User {
    id: number;
    email: string;
    first_name: string;
    last_name: string;
    role: string;
}

/**
 * Role Configuration Constants
 * ============================
 * 
 * Defines available user roles with descriptions for the business management system.
 * Each role has different permissions and access levels within the application.
 * 
 * Role Hierarchy (highest to lowest permissions):
 * 1. Admin - Full system access, can manage users and business settings
 * 2. Editor - Can create and edit products, limited admin access
 * 3. Approver - Can approve products for publication, read-only otherwise
 * 4. Viewer - Read-only access to products and basic features
 */
const ROLE_CHOICES = [
    { value: 'admin', label: 'Admin', description: 'Full access to all settings' },
    { value: 'editor', label: 'Editor', description: 'Can create and edit products' },
    { value: 'approver', label: 'Approver', description: 'Can only approve products' },
    { value: 'viewer', label: 'Viewer', description: 'Read-only access' },
];

/**
 * Business Management Component
 * =============================
 * 
 * Main component function that renders the business management interface.
 * Handles authentication, business selection, and provides tabbed navigation
 * for different management functions.
 */
export default function BusinessSettings() {
    // Authentication and navigation hooks
    const { user, logout } = useAuth();
    const router = useRouter();
    const pathname = usePathname();
    
    // Core business state management
    const [business, setBusiness] = useState<BusinessData | null>(null); // Currently selected business
    const [businesses, setBusinesses] = useState<BusinessData[]>([]); // All managed businesses
    const [activeTab, setActiveTab] = useState<'companies' | 'settings' | 'team'>('companies'); // Active tab
    const [users, setUsers] = useState<User[]>([]); // Team members for selected business

    // Business settings form state
    const [formData, setFormData] = useState({
        name: '',
        can_create_users: true,
        can_assign_roles: true
    });

    // User management form state
    const [userFormData, setUserFormData] = useState({
        email: '',
        first_name: '',
        last_name: '',
        role: 'viewer'
    });

    // Modal and UI state management
    const [showUserModal, setShowUserModal] = useState(false); // User creation/edit modal
    const [showBusinessModal, setShowBusinessModal] = useState(false); // Business creation modal
    
    // New business creation form state
    const [newBusinessData, setNewBusinessData] = useState({
        name: '',
        user_email: '',
        user_first_name: '',
        user_last_name: '',
        user_role: 'viewer'
    });
    
    // Additional state for user operations
    const [editingUser, setEditingUser] = useState<User | null>(null); // User being edited
    const [loading, setLoading] = useState(true); // Initial data loading state
    const [saving, setSaving] = useState(false); // Form submission state
    const [error, setError] = useState(''); // Error message display
    const [success, setSuccess] = useState(''); // Success message display

    /**
     * Authentication Guard and Initial Data Loading
     * =============================================
     * 
     * Ensures user is authenticated before accessing business management features.
     * Redirects unauthenticated users to login page.
     * Loads initial business and user data on component mount.
     */
    useEffect(() => {
        if (!user) {
            router.push('/login');
            return;
        }
        fetchBusiness();
        fetchUsers();
    }, [user, router]);

    /**
     * Fetch Team Members for Business
     * ===============================
     * 
     * Retrieves all team members for a specific business.
     * Supports both current business and specified business ID.
     * Handles both paginated and non-paginated API responses.
     * 
     * @param businessId - Optional business ID to fetch users for
     */
    const fetchUsers = async (businessId?: number) => {
        if (!businessId && !business?.id) return;
        try {
            const response = await api.get(`/auth/users/?business=${businessId || business?.id}`);
            const data = response.data.results || response.data;
            setUsers(data);
        } catch (err) {
            console.error('Error fetching users:', err);
        }
    };

    /**
     * Fetch Business Data and Auto-Selection
     * ======================================
     * 
     * Retrieves all businesses managed by the current user.
     * Automatically selects the first business if none is currently selected.
     * Handles both single business and multi-business scenarios.
     * Updates form data with selected business information.
     */
    const fetchBusiness = async () => {
        try {
            const response = await api.get('/auth/businesses/');
            const data = response.data.results || response.data;
            const bList = Array.isArray(data) ? data : [data];
            setBusinesses(bList);

            // Auto-select first business if none selected
            if (bList.length > 0 && !business) {
                const b = bList[0];
                setBusiness(b);
                setFormData({
                    name: b.name,
                    can_create_users: b.can_create_users,
                    can_assign_roles: b.can_assign_roles
                });
                fetchUsers(b.id);
            }
        } catch (err) {
            console.error('Error fetching business:', err);
            setError('Failed to load business details');
        } finally {
            setLoading(false);
        }
    };

    /**
     * Handle Business Settings Form Submission
     * ========================================
     * 
     * Updates business settings including name and capability permissions.
     * Provides user feedback through loading states and success/error messages.
     * Refreshes business data after successful update.
     */
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

    /**
     * Handle User Creation and Editing
     * ================================
     * 
     * Processes both new user creation and existing user updates.
     * For new users: Creates user and assigns to current business
     * For existing users: Updates user information and role
     * Provides appropriate success messages and refreshes user list.
     */
    const handleUserSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSaving(true);

        try {
            if (editingUser) {
                // Update existing user
                await api.patch(`/auth/users/${editingUser.id}/`, {
                    first_name: userFormData.first_name,
                    last_name: userFormData.last_name,
                    role: userFormData.role
                });
                setSuccess('User updated successfully');
            } else {
                // Create new user and assign to business
                await api.post('/auth/users/', {
                    ...userFormData,
                    business: business?.id
                });
                setSuccess('User invited successfully');
            }
            setShowUserModal(false);
            setEditingUser(null);
            setUserFormData({ email: '', first_name: '', last_name: '', role: 'viewer' });
            fetchUsers();
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to process user request');
        } finally {
            setSaving(false);
        }
    };

    /**
     * Handle Business Selection and Context Switching
     * ===============================================
     * 
     * Switches the active business context and updates all related data.
     * Updates form data with selected business information.
     * Automatically switches to settings tab and loads team members.
     */
    const handleSelectBusiness = (b: BusinessData) => {
        setBusiness(b);
        setFormData({
            name: b.name,
            can_create_users: b.can_create_users,
            can_assign_roles: b.can_assign_roles
        });
        setActiveTab('settings');
        fetchUsers(b.id);
    };

    /**
     * Handle New Business Creation
     * ============================
     * 
     * Creates a new business with an initial team member.
     * The initial user becomes the first admin of the new business.
     * Resets form data and refreshes business list after successful creation.
     */
    const handleCreateBusiness = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setError('');
        try {
            await api.post('/auth/businesses/', {
                name: newBusinessData.name,
                initial_user: {
                    email: newBusinessData.user_email,
                    first_name: newBusinessData.user_first_name,
                    last_name: newBusinessData.user_last_name,
                    role: newBusinessData.user_role
                }
            });
            setSuccess('Business and initial member created successfully');
            setShowBusinessModal(false);
            setNewBusinessData({
                name: '',
                user_email: '',
                user_first_name: '',
                user_last_name: '',
                user_role: 'viewer'
            });
            fetchBusiness();
        } catch (err: any) {
            setError(err.response?.data?.error || 'Failed to create business');
        } finally {
            setSaving(false);
        }
    };

    /**
     * Handle User Deletion
     * ====================
     * 
     * Removes a team member from the business after confirmation.
     * Uses browser confirmation dialog for destructive action.
     * Refreshes user list after successful deletion.
     */
    const handleDeleteUser = async (userId: number) => {
        if (!window.confirm('Are you sure you want to remove this user?')) return;
        try {
            await api.delete(`/auth/users/${userId}/`);
            setSuccess('User removed successfully');
            fetchUsers();
        } catch (err) {
            setError('Failed to remove user');
        }
    };

    /**
     * Handle User Logout
     * ==================
     * 
     * Logs out the current user and redirects to home page.
     * Clears authentication context and session data.
     */
    const handleLogout = () => {
        logout();
        router.push('/');
    };

    // Authentication guard - prevent rendering if user not authenticated
    if (!user) return null;

    return (
        <div className="flex h-screen bg-gray-50">
            {/* 
                Sidebar Navigation Component
                ============================
                
                Provides consistent navigation across the application with:
                - Role-based menu items (admin-only sections)
                - Active page highlighting
                - User information display
                - Logout functionality
                - Professional dark theme styling
            */}
            <div className="w-64 bg-[#001529] text-white shadow-lg flex flex-col transition-colors duration-200">
                {/* Application Header */}
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-white">Product Marketplace</h1>
                </div>

                {/* Navigation Menu with Role-Based Access Control */}
                <nav className="mt-6 flex-1 space-y-1">
                    {/* Admin Dashboard - Only visible to admin users */}
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

                    {/* User Management - Only visible to admin users */}
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

                    {/* Product Management - Available to all authenticated users */}
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

                    {/* Business Management - Currently active page */}
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

                    {/* AI Chatbot - Available to all authenticated users */}
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

                {/* User Information and Logout Section */}
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

            {/* 
                Main Content Area
                =================
                
                Contains the primary business management interface with:
                - Page header with title and description
                - Loading states for data fetching
                - Error and success message display
                - Tabbed content for different management functions
            */}
            <div className="flex-1 overflow-auto">
                <div className="p-8 max-w-6xl">
                    {/* Page Header */}
                    <div className="flex items-center justify-between mb-8">
                        <div>
                            <h2 className="text-3xl font-bold text-gray-900 tracking-tight">Business Management</h2>
                            <p className="text-gray-500 mt-1">Configure your organization and manage your team.</p>
                        </div>
                    </div>

                    {/* Loading State Display */}
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20">
                            <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-600 border-t-transparent"></div>
                            <p className="mt-4 text-gray-500 font-medium">Loading business data...</p>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {/* Success/Error Message Display */}
                            {(error || success) && (
                                <div className={`p-4 rounded-xl flex items-center gap-3 animate-in fade-in duration-300 ${error ? 'bg-red-50 border border-red-200 text-red-700' : 'bg-green-50 border border-green-200 text-green-700'
                                    }`}>
                                    {error ? <AlertCircle className="w-5 h-5 shrink-0" /> : <CheckCircle2 className="w-5 h-5 shrink-0" />}
                                    <p className="text-sm font-medium">{error || success}</p>
                                </div>
                            )}

                            {/* 
                                Companies Tab Content
                                =====================
                                
                                Displays all managed businesses in a card-based layout.
                                Allows users to view and select different businesses.
                                Provides option to create new businesses.
                            */}
                            {activeTab === 'companies' ? (
                                <div className="space-y-6">
                                    {/* Companies Tab Header with Add Company Button */}
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-xl font-bold text-gray-900">Your Managed Companies ({businesses.length})</h3>
                                        <button
                                            onClick={() => {
                                                setFormData({ ...formData, name: '' });
                                                setShowBusinessModal(true);
                                            }}
                                            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-bold hover:bg-blue-700 transition-all active:scale-95 shadow-lg shadow-blue-600/20"
                                        >
                                            <Building2 className="w-4 h-4" />
                                            Add Company
                                        </button>
                                    </div>

                                    {/* Business Cards Grid Layout */}
                                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                        {businesses.map((b) => (
                                            <div
                                                key={b.id}
                                                className={`p-6 rounded-2xl border-2 transition-all group ${business?.id === b.id ? 'border-blue-500 bg-blue-50/30' : 'border-gray-100 bg-white hover:border-gray-200 hover:shadow-lg'
                                                    }`}
                                            >
                                                {/* Business Card Header */}
                                                <div className="flex items-start justify-between mb-4">
                                                    <div className={`p-3 rounded-xl ${business?.id === b.id ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'}`}>
                                                        <Building2 className="w-6 h-6" />
                                                    </div>
                                                    {business?.id === b.id && (
                                                        <span className="bg-blue-100 text-blue-600 text-[10px] font-black uppercase px-2 py-1 rounded-md">Active</span>
                                                    )}
                                                </div>
                                                
                                                {/* Business Name */}
                                                <h4 className="text-lg font-bold text-gray-900 mb-1">{b.name}</h4>
                                                
                                                {/* Business Action Button */}
                                                <div className="flex items-center gap-4 mt-4">
                                                    <button
                                                        onClick={() => handleSelectBusiness(b)}
                                                        className={`flex-1 py-2 rounded-lg text-sm font-bold transition-all ${business?.id === b.id
                                                            ? 'bg-blue-600 text-white'
                                                            : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                                            }`}
                                                    >
                                                        View
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            ) : activeTab === 'settings' ? (
                                <div className="space-y-6">
                                    {/* Back to Companies Navigation */}
                                    <button
                                        onClick={() => setActiveTab('companies')}
                                        className="flex items-center gap-2 text-gray-500 hover:text-blue-600 font-bold transition-colors group mb-4"
                                    >
                                        <div className="p-2 bg-white rounded-lg border border-gray-100 group-hover:bg-blue-50 transition-colors">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                                            </svg>
                                        </div>
                                        Back to Companies
                                    </button>

                                    {/* Tab Navigation for Settings and Team */}
                                    <div className="flex items-center gap-4 mb-4">
                                        <button
                                            onClick={() => setActiveTab('settings')}
                                            className="px-6 py-2 rounded-xl text-sm font-bold transition-all bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                                        >
                                            General Settings
                                        </button>
                                        <button
                                            onClick={() => setActiveTab('team')}
                                            className="px-6 py-2 rounded-xl text-sm font-bold transition-all bg-white border border-gray-100 text-gray-500 hover:bg-gray-50"
                                        >
                                            Team Management
                                        </button>
                                    </div>

                                    {/* Business Settings Form Container */}
                                    <div className="bg-white rounded-2xl shadow-xl shadow-blue-900/5 border border-gray-100 overflow-hidden">
                                        <div className="p-8">
                                            {business ? (
                                                <form onSubmit={handleSubmit} className="space-y-8">
                                                    {/* Business Name Input */}
                                                    <div className="space-y-2">
                                                        <label className="text-sm font-bold text-gray-700 flex items-center gap-2">
                                                            <Building2 className="w-4 h-4" />
                                                            Legal Business Name
                                                        </label>
                                                        <input
                                                            type="text"
                                                            className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all"
                                                            value={formData.name}
                                                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                                            placeholder="e.g. Acme Corporation"
                                                            required
                                                        />
                                                    </div>

                                                    {/* Business Capabilities Configuration */}
                                                    <div className="space-y-4">
                                                        <label className="text-sm font-bold text-gray-700 flex items-center gap-2 uppercase tracking-wider">
                                                            <Shield className="w-4 h-4" />
                                                            Business Capabilities
                                                        </label>
                                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                                            {/* User Creation Capability Toggle */}
                                                            <div className={`p-5 rounded-2xl border-2 transition-all cursor-pointer flex items-start gap-4 ${formData.can_create_users ? 'border-blue-500 bg-blue-50/30' : 'border-gray-100 bg-gray-50/50'
                                                                }`} onClick={() => setFormData({ ...formData, can_create_users: !formData.can_create_users })}>
                                                                <div className={`p-2 rounded-lg ${formData.can_create_users ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                                                                    <UserPlus className="w-5 h-5" />
                                                                </div>
                                                                <div>
                                                                    <h4 className="font-bold text-gray-900">User Creation</h4>
                                                                    <p className="text-xs text-gray-500 mt-1">Allow your organization to scale by inviting new team members.</p>
                                                                </div>
                                                                <input type="checkbox" className="hidden" checked={formData.can_create_users} readOnly />
                                                            </div>

                                                            {/* Role Assignment Capability Toggle */}
                                                            <div className={`p-5 rounded-2xl border-2 transition-all cursor-pointer flex items-start gap-4 ${formData.can_assign_roles ? 'border-blue-500 bg-blue-50/30' : 'border-gray-100 bg-gray-50/50'
                                                                }`} onClick={() => setFormData({ ...formData, can_assign_roles: !formData.can_assign_roles })}>
                                                                <div className={`p-2 rounded-lg ${formData.can_assign_roles ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                                                                    <Shield className="w-5 h-5" />
                                                                </div>
                                                                <div>
                                                                    <h4 className="font-bold text-gray-900">Role Management</h4>
                                                                    <p className="text-xs text-gray-500 mt-1">Fine-tune permissions and access levels for all staff.</p>
                                                                </div>
                                                                <input type="checkbox" className="hidden" checked={formData.can_assign_roles} readOnly />
                                                            </div>
                                                        </div>
                                                    </div>

                                                    {/* Form Submission Button */}
                                                    <div className="flex justify-end pt-4">
                                                        <button
                                                            type="submit"
                                                            disabled={saving}
                                                            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-bold shadow-lg shadow-blue-600/20 active:scale-[0.98] transition-all disabled:opacity-70"
                                                        >
                                                            {saving ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-5 h-5" />}
                                                            {saving ? 'Applying Changes...' : 'Save Business'}
                                                        </button>
                                                    </div>
                                                </form>
                                            ) : (
                                                <div className="text-center py-12">
                                                    <p className="text-gray-500">Please select a company from the Companies tab first.</p>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-6">
                                    {/* Back to Companies Navigation */}
                                    <button
                                        onClick={() => setActiveTab('companies')}
                                        className="flex items-center gap-2 text-gray-500 hover:text-blue-600 font-bold transition-colors group mb-4"
                                    >
                                        <div className="p-2 bg-white rounded-lg border border-gray-100 group-hover:bg-blue-50 transition-colors">
                                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                                            </svg>
                                        </div>
                                        Back to Companies
                                    </button>

                                    {/* Tab Navigation for Settings and Team */}
                                    <div className="flex items-center gap-4 mb-4">
                                        <button
                                            onClick={() => setActiveTab('settings')}
                                            className="px-6 py-2 rounded-xl text-sm font-bold transition-all bg-white border border-gray-100 text-gray-500 hover:bg-gray-50"
                                        >
                                            General Settings
                                        </button>
                                        <button
                                            onClick={() => setActiveTab('team')}
                                            className="px-6 py-2 rounded-xl text-sm font-bold transition-all bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                                        >
                                            Team Management
                                        </button>
                                    </div>

                                    {business ? (
                                        <>
                                            {/* Team Management Header with Add Member Button */}
                                            <div className="flex items-center justify-between">
                                                <h3 className="text-xl font-bold text-gray-900">Team Members for {business.name} ({users.length})</h3>
                                                {/* Add Member Button - Only visible if business allows user creation */}
                                                {business.can_create_users && (
                                                    <button
                                                        onClick={() => {
                                                            setEditingUser(null);
                                                            setUserFormData({ email: '', first_name: '', last_name: '', role: 'viewer' });
                                                            setShowUserModal(true);
                                                        }}
                                                        className="flex items-center gap-2 bg-black text-white px-4 py-2 rounded-xl text-sm font-bold hover:bg-gray-800 transition-all active:scale-95"
                                                    >
                                                        <UserPlus className="w-4 h-4" />
                                                        Add Member
                                                    </button>
                                                )}
                                            </div>

                                            <div className="bg-white rounded-2xl shadow-xl shadow-blue-900/5 border border-gray-100 overflow-hidden">
                                                <div className="overflow-x-auto">
                                                    <table className="w-full text-left">
                                                        <thead>
                                                            <tr className="bg-gray-50/50 border-b border-gray-100">
                                                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Member</th>
                                                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider">Role</th>
                                                                <th className="px-6 py-4 text-xs font-bold text-gray-400 uppercase tracking-wider text-right">Actions</th>
                                                            </tr>
                                                        </thead>
                                                        <tbody className="divide-y divide-gray-50">
                                                            {users.map((u) => (
                                                                <tr key={u.id} className="hover:bg-gray-50/50 transition-colors">
                                                                    <td className="px-6 py-4">
                                                                        <div className="flex items-center gap-3">
                                                                            <div className="w-10 h-10 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold">
                                                                                {u.first_name[0]}{u.last_name[0]}
                                                                            </div>
                                                                            <div>
                                                                                <div className="font-bold text-gray-900">{u.first_name} {u.last_name}</div>
                                                                                <div className="text-xs text-gray-400">{u.email}</div>
                                                                            </div>
                                                                        </div>
                                                                    </td>
                                                                    <td className="px-6 py-4">
                                                                        <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${u.role === 'admin' ? 'bg-purple-100 text-purple-600' :
                                                                            u.role === 'editor' ? 'bg-blue-100 text-blue-600' :
                                                                                u.role === 'approver' ? 'bg-amber-100 text-amber-600' :
                                                                                    'bg-gray-100 text-gray-600'
                                                                            }`}>
                                                                            {u.role}
                                                                        </span>
                                                                    </td>
                                                                    <td className="px-6 py-4 text-right">
                                                                        <div className="flex items-center justify-end gap-2">
                                                                            {business.can_assign_roles && (
                                                                                <button
                                                                                    onClick={() => {
                                                                                        setEditingUser(u);
                                                                                        setUserFormData({
                                                                                            email: u.email,
                                                                                            first_name: u.first_name,
                                                                                            last_name: u.last_name,
                                                                                            role: u.role
                                                                                        });
                                                                                        setShowUserModal(true);
                                                                                    }}
                                                                                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                                                                                >
                                                                                    <Edit className="w-4 h-4" />
                                                                                </button>
                                                                            )}
                                                                            <button
                                                                                onClick={() => handleDeleteUser(u.id)}
                                                                                className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                                                                            >
                                                                                <Trash2 className="w-4 h-4" />
                                                                            </button>
                                                                        </div>
                                                                    </td>
                                                                </tr>
                                                            ))}
                                                        </tbody>
                                                    </table>
                                                </div>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="text-center py-12">
                                            <p className="text-gray-500">Please select a company from the Companies tab first.</p>
                                        </div>
                                    )}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Business Modal */}
            {showBusinessModal && (
                <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in zoom-in duration-200">
                    <div className="bg-white rounded-3xl w-full max-w-md shadow-2xl overflow-hidden">
                        <div className="px-8 py-6 bg-gray-50 border-b flex items-center justify-between">
                            <h3 className="text-xl font-bold text-gray-900">Add New Company</h3>
                            <button onClick={() => setShowBusinessModal(false)} className="text-gray-400 hover:text-gray-900 transition-colors">
                                <XCircle className="w-6 h-6" />
                            </button>
                        </div>

                        <form onSubmit={handleCreateBusiness} className="p-8 space-y-6 max-h-[80vh] overflow-y-auto">
                            <div className="space-y-4">
                                <h4 className="text-sm font-black uppercase text-gray-400 tracking-widest border-b pb-2">Business Information</h4>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase ml-1">Company Name</label>
                                    <div className="relative">
                                        <Building2 className="absolute left-4 top-3.5 w-4 h-4 text-gray-400" />
                                        <input
                                            required
                                            className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                            placeholder="e.g. Acme Ltd"
                                            value={newBusinessData.name}
                                            onChange={(e) => setNewBusinessData({ ...newBusinessData, name: e.target.value })}
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="space-y-4 pt-4">
                                <h4 className="text-sm font-black uppercase text-gray-400 tracking-widest border-b pb-2">Initial Team Member</h4>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="space-y-1.5">
                                        <label className="text-xs font-bold text-gray-500 uppercase ml-1">First Name</label>
                                        <input
                                            required
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                            placeholder="John"
                                            value={newBusinessData.user_first_name}
                                            onChange={(e) => setNewBusinessData({ ...newBusinessData, user_first_name: e.target.value })}
                                        />
                                    </div>
                                    <div className="space-y-1.5">
                                        <label className="text-xs font-bold text-gray-500 uppercase ml-1">Last Name</label>
                                        <input
                                            required
                                            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                            placeholder="Doe"
                                            value={newBusinessData.user_last_name}
                                            onChange={(e) => setNewBusinessData({ ...newBusinessData, user_last_name: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase ml-1">Email Address</label>
                                    <div className="relative">
                                        <Mail className="absolute left-4 top-3.5 w-4 h-4 text-gray-400" />
                                        <input
                                            required
                                            type="email"
                                            className="w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                            placeholder="john@example.com"
                                            value={newBusinessData.user_email}
                                            onChange={(e) => setNewBusinessData({ ...newBusinessData, user_email: e.target.value })}
                                        />
                                    </div>
                                </div>

                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase ml-1">Role</label>
                                    <div className="grid grid-cols-2 gap-2">
                                        {ROLE_CHOICES.map((role) => (
                                            <label key={role.value} className={`flex items-center gap-2 p-3 rounded-xl border-2 cursor-pointer transition-all ${newBusinessData.user_role === role.value ? 'border-blue-500 bg-blue-50/50' : 'border-gray-50 hover:bg-gray-50'
                                                }`}>
                                                <input
                                                    type="radio"
                                                    checked={newBusinessData.user_role === role.value}
                                                    onChange={() => setNewBusinessData({ ...newBusinessData, user_role: role.value })}
                                                    className="w-4 h-4 text-blue-600"
                                                />
                                                <span className="text-xs font-bold text-gray-900">{role.label}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="pt-6 flex gap-3 sticky bottom-0 bg-white pb-2 border-t mt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowBusinessModal(false)}
                                    className="flex-1 py-3 px-4 rounded-xl font-bold bg-gray-100 text-gray-600 hover:bg-gray-200 transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="flex-1 py-3 px-4 rounded-xl font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-50"
                                >
                                    {saving ? 'Creating...' : 'Create Company'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* User Modal */}
            {showUserModal && (
                <div className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in zoom-in duration-200">
                    <div className="bg-white rounded-3xl w-full max-w-lg shadow-2xl overflow-hidden">
                        <div className="px-8 py-6 bg-gray-50 border-b flex items-center justify-between">
                            <h3 className="text-xl font-bold text-gray-900">
                                {editingUser ? 'Edit Team Member' : 'Invite New Member'}
                            </h3>
                            <button onClick={() => setShowUserModal(false)} className="text-gray-400 hover:text-gray-900 transition-colors">
                                <XCircle className="w-6 h-6" />
                            </button>
                        </div>

                        <form onSubmit={handleUserSubmit} className="p-8 space-y-6">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase ml-1">First Name</label>
                                    <input
                                        required
                                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                        value={userFormData.first_name}
                                        onChange={(e) => setUserFormData({ ...userFormData, first_name: e.target.value })}
                                    />
                                </div>
                                <div className="space-y-1.5">
                                    <label className="text-xs font-bold text-gray-500 uppercase ml-1">Last Name</label>
                                    <input
                                        required
                                        className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                                        value={userFormData.last_name}
                                        onChange={(e) => setUserFormData({ ...userFormData, last_name: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-xs font-bold text-gray-500 uppercase ml-1">Email Address</label>
                                <div className="relative">
                                    <Mail className="absolute left-4 top-3.5 w-4 h-4 text-gray-400" />
                                    <input
                                        required
                                        type="email"
                                        disabled={!!editingUser}
                                        className={`w-full pl-11 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all ${editingUser ? 'bg-gray-100 text-gray-500' : ''
                                            }`}
                                        value={userFormData.email}
                                        onChange={(e) => setUserFormData({ ...userFormData, email: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="space-y-1.5">
                                <label className="text-xs font-bold text-gray-500 uppercase ml-1">Assign Role</label>
                                <div className="grid grid-cols-1 gap-3">
                                    {ROLE_CHOICES.map((role) => (
                                        <label key={role.value} className={`flex items-start gap-3 p-3 rounded-xl border-2 cursor-pointer transition-all ${userFormData.role === role.value ? 'border-blue-500 bg-blue-50/50' : 'border-gray-50 hover:bg-gray-50'
                                            }`}>
                                            <input
                                                type="radio"
                                                className="mt-1"
                                                checked={userFormData.role === role.value}
                                                onChange={() => setUserFormData({ ...userFormData, role: role.value })}
                                            />
                                            <div>
                                                <div className="text-sm font-bold text-gray-900">{role.label}</div>
                                                <div className="text-[10px] text-gray-500">{role.description}</div>
                                            </div>
                                        </label>
                                    ))}
                                </div>
                            </div>

                            <div className="pt-4 flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => setShowUserModal(false)}
                                    className="flex-1 py-3 px-4 rounded-xl font-bold bg-gray-100 text-gray-600 hover:bg-gray-200 transition-all"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={saving}
                                    className="flex-1 py-3 px-4 rounded-xl font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-600/20 active:scale-95 transition-all disabled:opacity-50"
                                >
                                    {saving ? 'Processing...' : (editingUser ? 'Save Updates' : 'Send Invite')}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
