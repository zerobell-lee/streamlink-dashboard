import React from 'react';
import { Monitor } from 'lucide-react';
import Image from 'next/image';

export const getPlatformIcon = (platform: string, size: 'sm' | 'md' | 'lg' = 'md') => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5', 
    lg: 'w-6 h-6'
  };

  const sizeClass = sizeClasses[size];

  switch (platform.toLowerCase()) {
    case 'twitch':
      return <Image src="/twitch.svg" alt="Twitch" width={size === 'sm' ? 16 : size === 'md' ? 20 : 24} height={size === 'sm' ? 16 : size === 'md' ? 20 : 24} className={sizeClass} />;
    case 'youtube':
      return <Image src="/youtube.svg" alt="YouTube" width={size === 'sm' ? 16 : size === 'md' ? 20 : 24} height={size === 'sm' ? 16 : size === 'md' ? 20 : 24} className={sizeClass} />;
    case 'sooplive':
      return <Image src="/soop_logo.svg" alt="Sooplive" width={size === 'sm' ? 16 : size === 'md' ? 20 : 24} height={size === 'sm' ? 16 : size === 'md' ? 20 : 24} className={sizeClass} />;
    case 'chzzk':
      return <Image src="/chzzk.png" alt="Chzzk" width={size === 'sm' ? 16 : size === 'md' ? 20 : 24} height={size === 'sm' ? 16 : size === 'md' ? 20 : 24} className={sizeClass} />;
    default:
      return <Monitor className={`${sizeClass} text-gray-600`} />;
  }
};