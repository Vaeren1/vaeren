import { Button } from "@/components/ui/button";
import { useLogout } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/stores/auth-store";
import { Link, Outlet } from "react-router-dom";

export function AppShell() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between">
          <Link to="/mitarbeiter" className="text-xl font-semibold">
            Vaeren
          </Link>
          <nav className="flex items-center gap-4">
            <Link
              to="/mitarbeiter"
              className="text-sm font-medium hover:underline"
            >
              Mitarbeiter
            </Link>
            <Link
              to="/schulungen"
              className="text-sm font-medium hover:underline"
            >
              Schulungen
            </Link>
            <Link
              to="/meldungen"
              className="text-sm font-medium hover:underline"
            >
              HinSchG
            </Link>
            <Link
              to="/mfa-setup"
              className="text-sm font-medium hover:underline"
            >
              MFA
            </Link>
            <span className="text-sm text-muted-foreground">{user?.email}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => logout.mutate()}
              disabled={logout.isPending}
            >
              Abmelden
            </Button>
          </nav>
        </div>
      </header>
      <main className="container py-8">
        <Outlet />
      </main>
    </div>
  );
}
