'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import LoginForm from '@/components/LoginForm';

export default function LoginPage() {
  const router = useRouter();

  useEffect(() => {
    // Security: Remove sensitive information from URL (username, password, etc.)
    const url = new URL(window.location.href);
    const sensitiveParams = ['username', 'password', 'pwd', 'user', 'email', 'token'];
    let hasSensitiveParams = false;

    sensitiveParams.forEach(param => {
      if (url.searchParams.has(param)) {
        url.searchParams.delete(param);
        hasSensitiveParams = true;
      }
    });

    if (hasSensitiveParams) {
      // Replace URL history to completely remove sensitive parameters if found
      window.history.replaceState({}, '', url.pathname);
      console.warn('Sensitive parameters detected in URL and removed for security');
    }
  }, []);

  return <LoginForm />;
}