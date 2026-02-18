'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register } from '@/lib/auth';
import { useAuth } from '@/contexts/AuthContext';
import { Building2, User as UserIcon, ShieldCheck, Mail, Lock, UserCircle } from 'lucide-react';

export default function Register() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'admin',
    business_name: '',
    can_create_users: true,
    can_assign_roles: true,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { setUser } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await register(formData);
      setUser(response.user);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData({ ...formData, [name]: checked });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  return (
    <div className="min-h-screen bg-[#f8fafc] flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-xl shadow-blue-900/5 overflow-hidden border border-gray-100">
        <div className="bg-[#001529] px-8 py-10 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600 mb-4 shadow-lg shadow-blue-600/20">
            <Building2 className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight">
            Register Your Business
          </h2>
          <p className="mt-2 text-blue-200/80">
            Set up your organization and start managing products in minutes.
          </p>
        </div>

        <form className="p-8 md:p-10 space-y-10" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-xl flex items-center gap-3 animate-shake">
              <span className="shrink-0 w-2 h-2 rounded-full bg-red-500" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Section 1: Administrator Details */}
          <div className="space-y-6">
            <div className="flex items-center gap-3 pb-2 border-b border-gray-100">
              <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                <UserIcon className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Administrator Information</h3>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-gray-700 ml-1">First Name</label>
                <input
                  name="first_name"
                  type="text"
                  required
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
                  placeholder="e.g. John"
                  value={formData.first_name}
                  onChange={handleChange}
                />
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-gray-700 ml-1">Last Name</label>
                <input
                  name="last_name"
                  type="text"
                  required
                  className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
                  placeholder="e.g. Doe"
                  value={formData.last_name}
                  onChange={handleChange}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-gray-700 ml-1">Email Address</label>
                <div className="relative group">
                  <Mail className="absolute left-4 top-3.5 w-5 h-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                  <input
                    name="email"
                    type="email"
                    required
                    className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
                    placeholder="john@example.com"
                    value={formData.email}
                    onChange={handleChange}
                  />
                </div>
              </div>
              <div className="space-y-1.5">
                <label className="text-sm font-semibold text-gray-700 ml-1">Role / Position</label>
                <div className="relative group">
                  <UserCircle className="absolute left-4 top-3.5 w-5 h-5 text-gray-400 pointer-events-none transition-colors" />
                  <select
                    name="role"
                    className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all appearance-none cursor-pointer"
                    value={formData.role}
                    onChange={handleChange}
                  >
                    <option value="admin">Administrator - Full Root Access</option>
                    <option value="editor">Editor - Manage Products</option>
                    <option value="approver">Approver - Product Reviewer</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700 ml-1">Account Password</label>
              <div className="relative group">
                <Lock className="absolute left-4 top-3.5 w-5 h-5 text-gray-400 group-focus-within:text-blue-500 transition-colors" />
                <input
                  name="password"
                  type="password"
                  required
                  minLength={8}
                  className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
                  placeholder="Min. 8 characters"
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>
            </div>
          </div>

          {/* Section 2: Business details & Capabilities */}
          <div className="space-y-6">
            <div className="flex items-center gap-3 pb-2 border-b border-gray-100">
              <div className="p-2 bg-blue-50 rounded-lg text-blue-600">
                <Building2 className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-gray-900">Business Details</h3>
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-semibold text-gray-700 ml-1">Legal Business Name</label>
              <input
                name="business_name"
                type="text"
                required
                className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all placeholder:text-gray-400"
                placeholder="e.g. Acme Corp Inc."
                value={formData.business_name}
                onChange={handleChange}
              />
            </div>

            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-blue-600" />
                <p className="text-sm font-bold text-gray-700 uppercase tracking-wider">Business Capabilities</p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <label className="flex items-start gap-4 p-4 border border-gray-100 rounded-2xl bg-gray-50/50 cursor-pointer hover:bg-white hover:shadow-md hover:border-blue-100 transition-all group">
                  <div className="flex items-center h-5 mt-1">
                    <input
                      name="can_create_users"
                      type="checkbox"
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                      checked={formData.can_create_users}
                      onChange={handleChange}
                    />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900 group-hover:text-blue-600 transition-colors">Create Users</p>
                    <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">Allow your business to add team members later.</p>
                  </div>
                </label>

                <label className="flex items-start gap-4 p-4 border border-gray-100 rounded-2xl bg-gray-50/50 cursor-pointer hover:bg-white hover:shadow-md hover:border-blue-100 transition-all group">
                  <div className="flex items-center h-5 mt-1">
                    <input
                      name="can_assign_roles"
                      type="checkbox"
                      className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                      checked={formData.can_assign_roles}
                      onChange={handleChange}
                    />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900 group-hover:text-blue-600 transition-colors">Assign Roles</p>
                    <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">Allow managing permissions and user roles.</p>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <div className="pt-4 space-y-4">
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center items-center gap-3 py-4 border border-transparent text-lg font-bold rounded-2xl text-white bg-blue-600 hover:bg-blue-700 shadow-xl shadow-blue-600/20 active:scale-[0.98] transition-all disabled:opacity-50"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : null}
              {loading ? 'Submitting Details...' : 'Complete Registration'}
            </button>

            <div className="text-center">
              <p className="text-sm text-gray-500">
                Already have an account?{' '}
                <Link href="/login" className="text-blue-600 font-bold hover:text-blue-800 transition-colors">
                  Sign in here
                </Link>
              </p>
            </div>
          </div>
        </form>
      </div>

      {/* Background decoration */}
      <div className="fixed top-0 left-0 w-full h-full pointer-events-none -z-10 bg-[radial-gradient(circle_at_50%_0%,#eff6ff_0%,transparent_50%),radial-gradient(circle_at_0%_100%,#eff6ff_0%,transparent_50%)]" />
    </div>
  );
}
