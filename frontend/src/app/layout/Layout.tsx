import { useLiveFeed } from '@/core/ws';
import { AppSidebar } from './AppSidebar';
import { Topbar } from './Topbar';

export function Layout({ children }: { children: React.ReactNode }) {
  useLiveFeed();

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Topbar />
      <div className="flex flex-1 overflow-hidden">
        <AppSidebar />
        <main className="flex-1 overflow-y-auto p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
