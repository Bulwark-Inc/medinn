'use client';

import { useState } from 'react';
import { forgotPassword } from '@/features/auth/services/authService';
import Link from 'next/link';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);
    setLoading(true);

    try {
      await forgotPassword(email);
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to send reset email. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-2 text-center">
          Forgot Password
        </h1>
        <p className="text-gray-600 text-sm text-center mb-6">
          Enter your email address and we'll send you a link to reset your password.
        </p>

        {success ? (
          <div className="bg-green-50 border border-green-200 rounded-md p-6 text-center">
            <svg className="mx-auto h-12 w-12 text-green-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            <h2 className="text-lg font-semibold text-green-800 mb-2">
              Email Sent!
            </h2>
            <p className="text-sm text-green-700 mb-4">
              Check your email for a link to reset your password. The link will expire in 1 hour.
            </p>
            <p className="text-xs text-gray-600 mb-4">
              If you don't see the email, check your spam folder.
            </p>
            <Link
              href="/login"
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium"
            >
              Back to Login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                placeholder="you@example.com"
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-md transition duration-200 disabled:opacity-60"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>

            <div className="text-sm text-center text-gray-600">
              <Link
                href="/login"
                className="text-indigo-600 hover:text-indigo-800 font-medium"
              >
                Back to Login
              </Link>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}