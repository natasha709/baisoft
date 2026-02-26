/**
 * Change Password Page Component - Secure Password Update Interface
 * ================================================================
 * 
 * This component provides a secure interface for users to change their passwords.
 * It's primarily used in the invitation system where users receive temporary
 * passwords and must set their own secure passwords on first login.
 * 
 * Key Features:
 * - Secure password change workflow
 * - Real-time password strength indicator
 * - Password confirmation validation
 * - Professional security-focused design
 * - Integration with invitation system
 * - Automatic redirection after successful change
 * - Comprehensive security warnings and guidelines
 * 
 * Use Cases:
 * 1. New users with temporary passwords (primary use case)
 * 2. Users wanting to update their existing passwords
 * 3. Security-mandated password changes
 * 
 * Security Features:
 * - Current password verification
 * - Password strength validation
 * - Password confirmation matching
 * - Minimum length requirements
 * - Clear security guidelines for users
 * - Temporary password expiration handling
 * 
 * User Experience:
 * - Clear instructions and warnings
 * - Visual password strength feedback
 * - Helpful error messages
 * - Professional security-focused design
 * - Responsive layout for all devices
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import api from '@/lib/api';

export default function ChangePassword() {
  // Authentication hook
  const { user } = useAuth();                                // Get current user data
  const router = useRouter();                                // Next.js router for navigation
  
  // Form state management
  const [formData, setFormData] = useState({
    old_password: '',                                        // Current password (temporary for new users)
    new_password: '',                                        // User's chosen new password
    confirm_password: '',                                    // Password confirmation for validation
  });
  
  // UI state management
  const [error, setError] = useState('');                    // Error message display
  const [loading, setLoading] = useState(false);             // Loading state during password change
  const [passwordStrength, setPasswordStrength] = useState(''); // Password strength indicator

  /**
   * Password Strength Checker
   * 
   * Evaluates password strength based on length and character complexity.
   * Provides real-time feedback to help users create secure passwords.
   * 
   * Strength Levels:
   * - Too short: Less than 8 characters
   * - Weak: 8-9 characters, basic requirements
   * - Medium: 10+ characters but missing character types
   * - Strong: 10+ characters with uppercase, lowercase, and numbers
   * 
   * @param password - Password to evaluate
   * @returns String indicating password strength level
   */
  const checkPasswordStrength = (password: string) => {
    if (password.length < 8) return 'Too short';
    if (password.length < 10) return 'Weak';
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
      return 'Medium';
    }
    return 'Strong';
  };

  /**
   * Handle Password Input Change
   * 
   * Updates the new password field and recalculates password strength
   * in real-time to provide immediate feedback to the user.
   * 
   * @param e - Input change event
   */
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newPassword = e.target.value;
    setFormData({ ...formData, new_password: newPassword });
    setPasswordStrength(checkPasswordStrength(newPassword));
  };

  /**
   * Handle Password Change Form Submission
   * 
   * Processes the password change request with comprehensive validation
   * and error handling. This is critical for the invitation system security.
   * 
   * Validation Steps:
   * 1. Client-side validation (password match, length)
   * 2. Server-side validation (current password, expiry)
   * 3. Password update and security flag clearing
   * 4. Automatic redirection to dashboard
   * 
   * Security Features:
   * - Current password verification
   * - Temporary password expiration checking
   * - Password change requirement flag clearing
   * - Role-based redirection
   * 
   * @param e - Form submission event
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Client-side validation: passwords must match
    if (formData.new_password !== formData.confirm_password) {
      setError('New passwords do not match');
      return;
    }

    // Client-side validation: minimum password length
    if (formData.new_password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      // Send password change request to backend
      await api.post('/auth/change-password/', formData);
      
      // Redirect based on user role after successful password change
      const roleRoutes: Record<string, string> = {
        admin: '/dashboard',
        editor: '/dashboard',
        approver: '/dashboard',
        viewer: '/dashboard',
      };
      
      router.push(roleRoutes[user?.role || 'viewer']);
    } catch (err: any) {
      // Display user-friendly error message
      setError(err.response?.data?.error || 'Failed to change password');
    } finally {
      // Always clear loading state
      setLoading(false);
    }
  };

  /**
   * Get Password Strength Color
   * 
   * Returns appropriate CSS color class based on password strength level.
   * Provides visual feedback to help users understand password security.
   * 
   * @returns CSS color class string
   */
  const getStrengthColor = () => {
    switch (passwordStrength) {
      case 'Strong': return 'text-green-600';      // Green for strong passwords
      case 'Medium': return 'text-yellow-600';     // Yellow for medium passwords
      case 'Weak': return 'text-orange-600';       // Orange for weak passwords
      default: return 'text-red-600';              // Red for too short/invalid
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Change Your Password
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            For security reasons, you must change your temporary password before continuing.
          </p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Password Change Required
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>Your temporary password will expire in 7 days. Please create a strong, unique password.</p>
              </div>
            </div>
          </div>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="old_password" className="block text-sm font-medium text-gray-700">
                Current (Temporary) Password
              </label>
              <input
                id="old_password"
                name="old_password"
                type="password"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter your temporary password"
                value={formData.old_password}
                onChange={(e) => setFormData({ ...formData, old_password: e.target.value })}
              />
            </div>

            <div>
              <label htmlFor="new_password" className="block text-sm font-medium text-gray-700">
                New Password
              </label>
              <input
                id="new_password"
                name="new_password"
                type="password"
                required
                minLength={8}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Enter your new password"
                value={formData.new_password}
                onChange={handlePasswordChange}
              />
              {formData.new_password && (
                <p className={`mt-1 text-sm ${getStrengthColor()}`}>
                  Password strength: {passwordStrength}
                </p>
              )}
            </div>

            <div>
              <label htmlFor="confirm_password" className="block text-sm font-medium text-gray-700">
                Confirm New Password
              </label>
              <input
                id="confirm_password"
                name="confirm_password"
                type="password"
                required
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Confirm your new password"
                value={formData.confirm_password}
                onChange={(e) => setFormData({ ...formData, confirm_password: e.target.value })}
              />
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
            <h4 className="text-sm font-medium text-blue-800 mb-2">Password Requirements:</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• At least 8 characters long</li>
              <li>• Different from your temporary password</li>
              <li>• Mix of uppercase, lowercase, and numbers (recommended)</li>
            </ul>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Changing Password...' : 'Change Password'}
          </button>
        </form>
      </div>
    </div>
  );
}
