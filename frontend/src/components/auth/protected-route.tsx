import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { useCurrentUser } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/stores/auth-store";

interface Props {
  children: ReactNode;
}

export function ProtectedRoute({ children }: Props) {
  const ephemeralToken = useAuthStore((s) => s.ephemeralToken);
  const { data: user, isLoading, isError, error } = useCurrentUser();

  if (ephemeralToken) {
    return <Navigate to="/mfa-challenge" replace />;
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-muted-foreground">
        Lade Sitzung …
      </div>
    );
  }

  if (isError || !user) {
    const status =
      error && "status" in error ? (error as { status?: number }).status : 0;
    if (status === 401 || status === 403 || !user) {
      return <Navigate to="/login" replace />;
    }
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-destructive">
        Sitzungsfehler. Bitte neu laden.
      </div>
    );
  }

  return <>{children}</>;
}
