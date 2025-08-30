import DashboardLayout from '@/components/DashboardLayout';
import Dashboard from '@/components/Dashboard';

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <Dashboard />
        </div>
      </div>
    </DashboardLayout>
  );
}