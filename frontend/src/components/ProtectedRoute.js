'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

const ProtectedRoute = ({ children }) => {
  const { user, fetchUser } = useAuth();
  const router = useRouter();
  const [loading, setLoading] = useState(true); // Track loading state

  useEffect(() => {
    // If user is null, fetch the user
    if (user === null) {
      fetchUser().finally(() => setLoading(false));  // Fetch user and then stop loading
    } else {
      setLoading(false);  // If user is already set, stop loading
    }
  }, [user, fetchUser]);

  useEffect(() => {
    if (user === null && !loading) {
      router.push('/login');  // Redirect to login if no user after loading
    }
  }, [user, router, loading]);

  if (loading) {
    return <div>Loading...</div>; // Optionally, show a loading spinner or message
  }

  return <>{children}</>;  // Render protected content
};

export default ProtectedRoute;
