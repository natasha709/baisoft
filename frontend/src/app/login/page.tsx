'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Lock, Eye, EyeOff, Signal } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { login } from '@/lib/auth';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { setUser } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await login(email, password);
      // The login function in lib/auth usually returns { user, tokens } or similar structure
      // Adjust based on your actual API response structure if needed
      if (response && response.user) {
        setUser(response.user);

        if (response.user.password_change_required) {
          router.push('/change-password');
        } else {
          router.push('/dashboard');
        }
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.response?.data?.error || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex flex-col items-center justify-center p-4">
      {/* Background Image Placeholder - In production, replace with actual image */}
      <div
        className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: 'url("https://w0.peakpx.com/wallpaper/594/433/HD-wallpaper-white-silk-texture-white-fabric-background-silk-texture-satin-white-fabric-texture.jpg")', // White silk abstract background
        }}
      >
        <div className="absolute inset-0 bg-white/10 backdrop-blur-sm"></div>
      </div>

      <div className="relative z-10 w-full max-w-[400px]">
        <div className="bg-[#fafafa]/80 backdrop-blur-md border border-white/40 rounded-2xl shadow-2xl p-8 w-full">
          {/* Header Section */}
          <div className="flex flex-col items-center mb-6">
            <div className="w-16 h-16 bg-[#001529] rounded-full flex items-center justify-center mb-4 shadow-lg">
              <Lock className="w-8 h-8 text-white" />
            </div>

            <h1 className="text-2xl font-bold text-gray-800 mb-1">Welcome Back</h1>
            <p className="text-gray-500 text-sm mb-4">Sign in to continue</p>

            <div className="px-4 py-1.5 bg-green-50 rounded-full flex items-center gap-2 border border-green-100">
              <Signal className="w-4 h-4 text-green-600" />
              <span className="text-sm font-medium text-green-700">Online</span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm text-center border border-red-100">
                {error}
              </div>
            )}

            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-gray-700 ml-1">
                Email
              </label>
              <div className="relative">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-blue-50/50 border border-transparent focus:bg-white focus:border-[#001529] focus:ring-4 focus:ring-blue-500/10 transition-all outline-none text-gray-800 placeholder-gray-400"
                  placeholder="name@example.com"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-gray-700 ml-1">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-blue-50/50 border border-transparent focus:bg-white focus:border-[#001529] focus:ring-4 focus:ring-blue-500/10 transition-all outline-none text-gray-800 placeholder-gray-400 pr-12"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="flex justify-end pt-1">
              <Link
                href="/forgot-password"
                className="text-sm font-medium text-[#001529] hover:text-blue-800 hover:underline transition-colors"
              >
                Forgot Password?
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-[#001529] hover:bg-[#002140] text-white font-semibold py-3.5 rounded-xl shadow-lg shadow-blue-900/20 active:scale-[0.98] transition-all disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>

            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-100"></div>
              </div>
            </div>

            <div className="text-center pb-2">
              <Link
                href="/privacy-policy"
                className="text-sm font-medium text-[#001529] hover:text-blue-800 transition-colors"
              >
                Privacy Policy
              </Link>
            </div>
          </form>
        </div>

        {/* Footer outside the card */}
        <div className="text-center mt-8">
          <p className="text-gray-500 text-xs font-medium tracking-wide drop-shadow-sm">
            Secure Access • v1.0
          </p>
        </div>
      </div>
    </div>
  );
}
