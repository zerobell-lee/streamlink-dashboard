import DashboardLayout from '@/components/DashboardLayout';
import { FileText } from 'lucide-react';

export default function LogsPage() {
  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-foreground flex items-center">
              <FileText className="h-8 w-8 mr-3 text-amber-500" />
              Log Management
            </h1>
            <p className="mt-2 text-muted-foreground">
              Monitor, search, and analyze application logs
            </p>
          </div>

          <div className="bg-card rounded-lg shadow-sm border border-border">
            <div className="p-6">
              <p className="text-muted-foreground text-center">
                Log management functionality will be implemented here.
              </p>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}