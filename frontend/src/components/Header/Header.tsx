import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';

export function Header() {
  return (
    <header className="border-b bg-background/95 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Link to="/" className="flex items-center gap-3">
          <span className="grid size-9 place-items-center rounded-lg bg-primary text-sm font-semibold text-primary-foreground">
            AI
          </span>
          <span>
            <span className="block text-base font-semibold leading-5">AI News Hub</span>
            <span className="block text-xs text-muted-foreground">Frontend foundation</span>
          </span>
        </Link>
        <Badge variant="outline">Home only</Badge>
      </div>
    </header>
  );
}
