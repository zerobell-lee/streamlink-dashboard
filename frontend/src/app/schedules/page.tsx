'use client';

import DashboardLayout from '@/components/DashboardLayout';
import RecordingSchedules from '@/components/RecordingSchedules';

export default function SchedulesPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <RecordingSchedules />
        </div>
      </div>
    </DashboardLayout>
  );
}