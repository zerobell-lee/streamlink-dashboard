import DashboardLayout from '@/components/DashboardLayout';
import SystemSettings from '@/components/SystemSettings';

export default function SystemPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="max-w-4xl mx-auto">
          <SystemSettings />
        </div>
      </div>
    </DashboardLayout>
  );
}