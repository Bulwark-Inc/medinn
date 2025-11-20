'use client';

import { useState } from 'react';
import { changePassword } from '@/features/auth/services/authService';
import ProtectedRoute from '@/components/ProtectedRoute';

export default function ChangePasswordPage() {
  const [formData, setFormData] = useState({
    old_password: '',
    new_password: '',
    new_password2: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    if (formData.new_password !== formData.new_password2) {
      setError('New passwords do not match');
      return;
    }

    setLoading(true);

    try {
      await changePassword(
        formData.old_password,
        formData.new_password,
        formData.new_password2
      );
      setSuccess(true);
      setFormData({
        old_password: '',
        new_password: '',
        new_password2: '',
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="max-w-2xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-6">Change Password</h1>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Form fields here */}
        </form>
      </div>
    </ProtectedRoute>
  );
}