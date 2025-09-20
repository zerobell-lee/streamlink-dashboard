"use client";

import { 
  BarChart3,
  Video, 
  Clock, 
  Settings,
  Film,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import clsx from 'clsx';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  isCollapsed?: boolean;
  onToggleCollapse?: () => void;
}

const menuItems = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: BarChart3,
    description: 'System overview',
    href: '/dashboard'
  },
  {
    id: 'recordings',
    label: 'Recordings',
    icon: Film,
    description: 'Manage recordings',
    href: '/recordings'
  },
  {
    id: 'schedules',
    label: 'Schedules',
    icon: Clock,
    description: 'Auto recording',
    href: '/schedules'
  },
  {
    id: 'platforms',
    label: 'Platforms',
    icon: Video,
    description: 'API configurations',
    href: '/platforms'
  },
  {
    id: 'system',
    label: 'System',
    icon: Settings,
    description: 'System settings',
    href: '/system'
  }
];

export default function Sidebar({ isOpen, onClose, isCollapsed = false, onToggleCollapse }: SidebarProps) {
  const pathname = usePathname();
  const version = process.env.NEXT_PUBLIC_APP_VERSION || '0.5.0';
  
  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={clsx(
        "fixed left-0 top-0 h-full bg-white border-r border-gray-200 z-50 transform transition-all duration-300 ease-in-out",
        isOpen ? "translate-x-0" : "-translate-x-full",
        "lg:translate-x-0 lg:static lg:z-auto",
        isCollapsed ? "w-20" : "w-64"
      )}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className={`p-4 border-b border-gray-200 flex items-center ${isCollapsed ? 'justify-center' : 'justify-between'}`}>
            {!isCollapsed && (
              <h2 className="text-lg font-semibold text-gray-900">Navigation</h2>
            )}
            {onToggleCollapse && (
              <button
                onClick={onToggleCollapse}
                className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors hidden lg:flex"
                title={isCollapsed ? "Expand sidebar" : "Collapse sidebar"}
              >
                {isCollapsed ? (
                  <ChevronRight className="h-4 w-4 text-gray-600" />
                ) : (
                  <ChevronLeft className="h-4 w-4 text-gray-600" />
                )}
              </button>
            )}
          </div>
          
          {/* Menu Items */}
          <nav className="flex-1 p-4 space-y-2">
            {menuItems.map((item) => {
              const Icon = item.icon;
              
              // Check if item is active based on pathname
              const normalizedPathname = pathname.endsWith('/') ? pathname.slice(0, -1) : pathname;
              const normalizedHref = item.href.endsWith('/') ? item.href.slice(0, -1) : item.href;
              const isActive = normalizedPathname === normalizedHref || pathname === item.href;
              
              const content = (
                <div className={clsx(
                  "w-full flex items-center rounded-lg transition-colors",
                  isCollapsed ? "px-2 py-4 justify-center" : "px-3 py-2 space-x-3",
                  isActive && !isCollapsed
                    ? "bg-blue-50 text-blue-700 border border-blue-200"
                    : isActive && isCollapsed
                    ? "text-blue-600"
                    : "text-gray-700 hover:bg-gray-50"
                )}>
                  <Icon className={isCollapsed ? "h-5 w-5" : "h-5 w-5"} />
                  {!isCollapsed && (
                    <div className="flex-1">
                      <div className="font-medium">{item.label}</div>
                      <div className="text-sm text-gray-500">{item.description}</div>
                    </div>
                  )}
                </div>
              );
              
              return (
                <Link 
                  key={item.id} 
                  href={item.href} 
                  onClick={onClose}
                  className="block"
                  title={isCollapsed ? `${item.label} - ${item.description}` : undefined}
                >
                  {content}
                </Link>
              );
            })}
          </nav>
          
          {/* Footer */}
          {!isCollapsed && (
            <div className="p-4 border-t border-gray-200">
              <div className="text-sm text-gray-500">
                <div className="font-medium">Streamlink Dashboard</div>
                <div>v{version}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
