import { Suspense } from 'react';
import { useRoutes } from 'react-router-dom';
import { AppErrorBoundary } from '@/components/AppErrorBoundary';
import { routes } from '@/routes';

function LoadingFallback() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-b-2 border-primary" />
    </div>
  );
}

function App() {
  const routeElement = useRoutes(routes);

  return (
    <AppErrorBoundary>
      <Suspense fallback={<LoadingFallback />}>{routeElement}</Suspense>
    </AppErrorBoundary>
  );
}

export default App;
