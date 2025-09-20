"use client";

import { useState } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { api } from '@/lib/api';
import { ThemeToggle } from '@/components/ThemeToggle';
import {
  Menu,
  User,
  Play,
  LogOut,
  ChevronDown
} from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { user, logout } = useAuthStore();

  const handleLogout = async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      console.warn('Logout API call failed, but proceeding with client logout');
    }
    logout();
    setUserMenuOpen(false);
  };



  return (
    <>
      <header className="bg-background border-b border-border px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Left side */}
          <div className="flex items-center space-x-4">
            {/* Mobile menu button - only show on small screens */}
            <button
              onClick={onMenuClick}
              className="lg:hidden p-2 hover:bg-accent hover:text-accent-foreground rounded-lg transition-colors"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Logo and title */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Play className="h-4 w-4 text-primary-foreground" />
              </div>
              <h1 className="text-xl font-semibold text-foreground hidden sm:block">
                Streamlink Dashboard
              </h1>
            </div>
          </div>

          {/* Right side - Theme toggle and User menu */}
          <div className="flex items-center space-x-3">
            {/* Theme toggle */}
            <ThemeToggle />

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setUserMenuOpen(!userMenuOpen)}
                className="flex items-center space-x-2 px-3 py-2 hover:bg-accent hover:text-accent-foreground rounded-lg transition-colors"
              >
                <User className="h-5 w-5" />
                <span className="text-sm hidden sm:block">{user?.username}</span>
                <ChevronDown className="h-4 w-4 text-muted-foreground" />
              </button>

              {userMenuOpen && (
                <div className="absolute right-0 mt-2 w-32 bg-popover rounded-md shadow-lg border border-border z-10">
                  <div className="py-1">
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-sm text-popover-foreground hover:bg-accent hover:text-accent-foreground flex items-center space-x-2"
                    >
                      <LogOut className="h-4 w-4" />
                      <span>Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>
    </>
  );
}
