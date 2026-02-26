/**
 * Forgot Password Page Component - Password Reset Interface
 * =========================================================
 * 
 * This component provides a password reset interface for users who have
 * forgotten their passwords. It follows standard security practices for
 * password recovery workflows.
 * 
 * Key Features:
 * - Email-based password reset request
 * - Professional security-focused design
 * - User-friendly success/error messaging
 * - Integration with backend password reset system
 * - Responsive design for all devices
 * - Security best practices implementation
 * 
 * Security Features:
 * - Email validation before submission
 * - Generic success message (doesn't reveal if email exists)
 * - Rate limiting protection (handled by backend)
 * - Secure token generation (handled by backend)
 * - No sensitive information exposure
 * 
 * User Flow:
 * 1. User enters their email address
 * 2. System sends password reset link to email (if account exists)
 * 3. User receives generic success message
 * 4. User checks email for reset instructions
 * 5. User follows link to reset password (separate flow)
 * 
 * Design Philosophy:
 * - Clean, professional appearance
 * - Clear instructions and expectations
 * - Security-focused messaging
 * - Consistent with login page design
 * - Accessibility-friendly interface
 * 
 * Note: This is currently a placeholder implementation.
 * The backend password reset endpoint needs to be implemented
 * for full functionality.
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Lock, Mail, ChevronLeft } from 'lucide-react';

export default function ForgotPassword() {
    // Form state management
    const [email, setEmail] = useState('');                    // User's email input
    const [loading, setLoading] = useState(false);             // Loading state during request
    const [success, setSuccess] = useState(false);             // Success state after submission
    const [error, setError] = useState('');                    // Error message display

    /**
     * Handle Password Reset Form Submission
     * 
     * Processes the password reset request with proper security practices.
     * Currently simulates the API call since the backend endpoint is not implemented.
     * 
     * Security Considerations:
     * - Generic success message regardless of whether email exists
     * - No information disclosure about account existence
     * - Rate limiting should be implemented on backend
     * - Secure token generation for reset links
     * 
     * TODO: Implement actual backend endpoint integration
     * 
     * @param e - Form submission event
     */
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        // TODO: Replace with actual API call when backend endpoint is implemented
        // Example implementation:
        // try {
        //     await api.post('/auth/forgot-password/', { email });
        //     setSuccess(true);
        // } catch (err: any) {
        //     setError('Failed to send reset link. Please try again.');
        // } finally {
        //     setLoading(false);
        // }

        // Simulate API call for now
        setTimeout(() => {
            setLoading(false);
            setSuccess(true);
        }, 1500);
    };

    return (
        <div className="min-h-screen relative flex flex-col items-center justify-center p-4">
            {/* Background Image Placeholder */}
            <div
                className="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat"
                style={{
                    backgroundImage: 'url("https://w0.peakpx.com/wallpaper/594/433/HD-wallpaper-white-silk-texture-white-fabric-background-silk-texture-satin-white-fabric-texture.jpg")',
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

                        <h1 className="text-2xl font-bold text-gray-800 mb-1">Forgot Password?</h1>
                        <p className="text-gray-500 text-sm mb-4 text-center">
                            Enter your email address to reset your password.
                        </p>
                    </div>

                    {!success ? (
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
                                        className="w-full px-4 py-3 rounded-xl bg-blue-50/50 border border-transparent focus:bg-white focus:border-[#001529] focus:ring-4 focus:ring-blue-500/10 transition-all outline-none text-gray-800 placeholder-gray-400 pl-10"
                                        placeholder="name@example.com"
                                    />
                                    <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                                        <Mail size={18} />
                                    </div>
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-[#001529] hover:bg-[#002140] text-white font-semibold py-3.5 rounded-xl shadow-lg shadow-blue-900/20 active:scale-[0.98] transition-all disabled:opacity-70 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Sending Link...' : 'Send Reset Link'}
                            </button>

                            <div className="relative my-6">
                                <div className="absolute inset-0 flex items-center">
                                    <div className="w-full border-t border-gray-100"></div>
                                </div>
                            </div>

                            <div className="text-center">
                                <Link
                                    href="/login"
                                    className="inline-flex items-center text-sm font-medium text-gray-600 hover:text-[#001529] transition-colors"
                                >
                                    <ChevronLeft size={16} className="mr-1" />
                                    Back to Login
                                </Link>
                            </div>
                        </form>
                    ) : (
                        <div className="text-center space-y-6">
                            <div className="bg-blue-50 text-blue-700 p-4 rounded-xl border border-blue-100 text-sm">
                                If an account exists for <strong>{email}</strong>, you will receive password reset instructions shortly.
                            </div>

                            <Link
                                href="/login"
                                className="inline-flex items-center justify-center w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-3.5 rounded-xl transition-all"
                            >
                                Back to Login
                            </Link>
                        </div>
                    )}
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
