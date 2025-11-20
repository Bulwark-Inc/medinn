'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { verifyEmail } from '@/features/auth/services/authService';
import { useAuth } from '@/contexts/AuthContext';
import Link from 'next/link';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refetchUser } = useAuth();
  
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [message, setMessage] = useState('');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage('Verification token is missing. Please check your email link.');
      return;
    }

    const verify = async () => {
      try {
        const result = await verifyEmail(token);
        setStatus('success');
        setMessage(result.message || 'Email verified successfully!');
        
        // Refetch user to update email_verified status
        await refetchUser();
        
        // Redirect to dashboard after 3 seconds
        setTimeout(() => {
          router.push('/dashboard');
        }, 3000);
      } catch (err) {
        setStatus('error');
        setMessage(err.message || 'Email verification failed. The token may be invalid or expired.');
      }
    };

    verify();
  }, [searchParams, refetchUser, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white shadow-md rounded-lg p-8 text-center">
        {status === 'verifying' && (
          <div>
            <div className="inline-block h-12 w-12 animate-spin rounded-full border-4 border-solid border-indigo-600 border-r-transparent mb-4"></div>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Verifying Email...
            </h1>
            <p className="text-gray-600">
              Please wait while we verify your email address.
            </p>
          </div>
        )}

        {status === 'success' && (
          <div>
            <svg className="mx-auto h-16 w-16 text-green-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Email Verified!
            </h1>
            <p className="text-gray-600 mb-4">
              {message}
            </p>
            <p className="text-sm text-gray-500">
              Redirecting to dashboard...
            </p>
          </div>
        )}

        {status === 'error' && (
          <div>
            <svg className="mx-auto h-16 w-16 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h1 className="text-2xl font-bold text-gray-800 mb-2">
              Verification Failed
            </h1>
            <p className="text-gray-600 mb-6">
              {message}
            </p>
            <div className="space-y-2">
              <Link
                href="/login"
                className="block w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-md transition duration-200"
              >
                Go to Login
              </Link>
              <p className="text-sm text-gray-500">
                Need help?{' '}
                <Link href="/register" className="text-indigo-600 hover:text-indigo-800">
                  Register again
                </Link>
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}