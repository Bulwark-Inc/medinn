'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import useRedirectIfAuthenticated from '@/utils/useRedirectIfAuthenticated';
import { resendVerificationEmail } from '@/features/auth/services/authService';
import Link from 'next/link';

export default function LoginPage() {
  useRedirectIfAuthenticated();
  
  const { login } = useAuth();
  const router = useRouter();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showEmailNotVerified, setShowEmailNotVerified] = useState(false);
  const [resendingEmail, setResendingEmail] = useState(false);
  const [resendSuccess, setResendSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setShowEmailNotVerified(false);
    setResendSuccess(false);
    setLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard');
    } catch (err) {
      // Check if error is about email verification
      if (err.message === 'EMAIL_NOT_VERIFIED') {
        setShowEmailNotVerified(true);
        setError('Your email is not verified. Please check your inbox or click below to resend the verification email.');
      } else {
        setError(err.message || 'Invalid email or password.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleResendVerification = async () => {
    setResendingEmail(true);
    setError('');
    setResendSuccess(false);

    try {
      await resendVerificationEmail(email);
      setResendSuccess(true);
      setShowEmailNotVerified(false);
    } catch (err) {
      setError(err.message || 'Failed to resend verification email.');
    } finally {
      setResendingEmail(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          Sign In
        </h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
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

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
              {error}
            </div>
          )}

          {showEmailNotVerified && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <p className="text-sm text-yellow-800 mb-2">
                Your email is not verified. Please check your inbox.
              </p>
              <button
                type="button"
                onClick={handleResendVerification}
                disabled={resendingEmail}
                className="text-sm text-indigo-600 hover:text-indigo-800 font-medium disabled:opacity-50"
              >
                {resendingEmail ? 'Sending...' : 'Resend verification email'}
              </button>
            </div>
          )}

          {resendSuccess && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md text-sm">
              Verification email sent! Please check your inbox.
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-md transition duration-200 disabled:opacity-60"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="text-sm text-center mt-4 text-gray-600 space-y-2">
          <p>
            <Link
              href="/forgot-password"
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Forgot your password?
            </Link>
          </p>
          <p>
            Don't have an account?{' '}
            <Link
              href="/register"
              className="text-indigo-600 hover:text-indigo-800 font-medium"
            >
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}