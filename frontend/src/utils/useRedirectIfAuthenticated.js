'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation'; // Use correct import based on your setup
import { useAuth } from '@/contexts/AuthContext';

const useRedirectIfAuthenticated = () => {
  const { user } = useAuth();
  const router = useRouter();
  const [isClient, setIsClient] = useState(false);

  // Only run on the client
  useEffect(() => {
    setIsClient(true);
  }, []);

  useEffect(() => {
    if (isClient && user) {
      router.push('/dashboard');
    }
  }, [user, isClient, router]);
};

export default useRedirectIfAuthenticated;
