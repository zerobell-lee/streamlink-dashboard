"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/auth-store';

export default function Home() {
  const { isAuthenticated, isHydrated } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Wait for hydration to complete before checking auth
    if (!isHydrated) return;

    // Temporary cleanup for legacy auth storage
    const legacyToken = localStorage.getItem('auth_token');
    if (legacyToken && !isAuthenticated) {
      localStorage.removeItem('auth_token');
      localStorage.removeItem('auth-storage');
    }

    if (!isAuthenticated) {
      router.push('/login');
    } else {
      // Redirect to dashboard
      router.push('/dashboard');
    }
  }, [isAuthenticated, isHydrated, router]);

  // Show loading while hydrating or redirecting
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="text-gray-600 mt-2">Loading...</p>
      </div>
    </div>
  );
}
