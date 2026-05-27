import { Outlet } from 'react-router-dom';
import { Header } from '@/components/Header';

export function Layout() {
  return (
    <div className="flex min-h-screen flex-col bg-background text-foreground">
      <Header />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="border-t bg-muted/30">
        <div className="mx-auto flex h-14 max-w-6xl items-center px-6">
          <p className="text-sm text-muted-foreground">© 2026 AI News Hub</p>
        </div>
      </footer>
    </div>
  );
}
