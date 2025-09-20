"use client";

import * as React from 'react';
import { useTheme } from 'next-themes';
import { Monitor, Moon, Sun } from 'lucide-react';
import clsx from 'clsx';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-9 h-9 rounded-lg border border-input bg-background flex items-center justify-center">
        <Sun className="h-4 w-4" />
      </div>
    );
  }

  const themes = [
    {
      name: 'light',
      label: 'Light',
      icon: Sun,
    },
    {
      name: 'dark',
      label: 'Dark',
      icon: Moon,
    },
    {
      name: 'system',
      label: 'System',
      icon: Monitor,
    },
  ];

  const currentTheme = themes.find(t => t.name === theme) || themes[0];
  const CurrentIcon = currentTheme.icon;

  return (
    <div className="relative">
      <button
        onClick={() => {
          const currentIndex = themes.findIndex(t => t.name === theme);
          const nextIndex = (currentIndex + 1) % themes.length;
          setTheme(themes[nextIndex].name);
        }}
        className={clsx(
          "w-9 h-9 rounded-lg border border-input bg-background hover:bg-accent hover:text-accent-foreground",
          "flex items-center justify-center transition-colors",
          "focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        )}
        title={`현재 테마: ${currentTheme.label} (클릭하여 전환)`}
      >
        <CurrentIcon className="h-4 w-4" />
        <span className="sr-only">테마 전환</span>
      </button>
    </div>
  );
}