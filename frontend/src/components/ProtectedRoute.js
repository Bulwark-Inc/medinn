'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

const ProtectedRoute = ({ children }) => {
  const { user, isLoading } = useAuth(); // Get user and loading state from context
  const router = useRouter();

  useEffect(() => {
    if (user === null && !isLoading) {
      router.push('/login'); // Redirect to login if no user is found after loading
    }
  }, [user, router, isLoading]);

  if (isLoading) {
    return <div>Loading...</div>; // Optionally, show a loading spinner or message
  }

  return <>{children}</>;  // Render protected content if user is authenticated
};

export default ProtectedRoute;