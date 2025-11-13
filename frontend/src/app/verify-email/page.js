'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import api from '@/utils/api';
import useRedirectIfAuthenticated from '@/utils/useRedirectIfAuthenticated';

export default function VerifyEmailPage() {
  useRedirectIfAuthenticated();

  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get('token');
  const [status, setStatus] = useState('Verifying...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const verify = async () => {
      if (!token) {
        setStatus('No token found.');
        setLoading(false);
        return;
      }

      try {
        await api.post('/verify-email/', { token });
        setStatus('Email verified successfully! Redirecting to login...');
        setLoading(false);

        // Redirect to login after 3 seconds
        setTimeout(() => router.push('/login'), 3000);
      } catch (err) {
        setStatus('Invalid or expired token.');
        setLoading(false);
      }
    };

    verify();
  }, [token, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="bg-white shadow-lg rounded-lg p-8 w-full max-w-md text-center">
        <h1 className="text-2xl font-semibold mb-4">Email Verification</h1>
        <p className="text-gray-700">{loading ? 'Verifying...' : status}</p>
      </div>
    </div>
  );
}
