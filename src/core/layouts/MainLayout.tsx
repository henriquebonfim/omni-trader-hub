import { TopBar } from './TopBar';
import { AppSidebar } from './AppSidebar';

interface MainLayoutProps {
  children: React.ReactNode;
  wsStatus: 'connecting' | 'open' | 'closed';
}

export function MainLayout({ children, wsStatus }: MainLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      <TopBar wsStatus={wsStatus} />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
