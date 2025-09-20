'use client';

import DashboardLayout from '@/components/DashboardLayout';
import PlatformManagement from '@/components/PlatformManagement';

export default function PlatformsPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <PlatformManagement />
        </div>
      </div>
    </DashboardLayout>
  );
}