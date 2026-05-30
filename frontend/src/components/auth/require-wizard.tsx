/**
 * Erst-Login-Redirect für den Onboarding-Wizard (Feature 1, §3).
 *
 * Hängt innerhalb des authentifizierten Bereichs. Wenn der eingeloggte User
 * Geschäftsführer:in ist UND der Wizard noch nicht durchlaufen wurde
 * (`osint_status.wizard_durchlaufen === false`), wird einmalig auf
 * `/onboarding-wizard` umgeleitet. Alle anderen Rollen / bereits durchlaufene
 * Wizards passieren ungehindert.
 */
import { onboarding } from "@/lib/api/onboarding";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

interface Props {
  children: ReactNode;
}

export function RequireWizard({ children }: Props) {
  const role = useAuthStore((s) => s.user?.tenant_role);
  const istGF = role === "geschaeftsfuehrer";
  const location = useLocation();

  const { data, isLoading } = useQuery({
    queryKey: ["onboarding-status"],
    queryFn: () => onboarding.status(),
    enabled: istGF,
    // Status ändert sich selten — kein aggressives Refetchen nötig.
    staleTime: 5 * 60 * 1000,
  });

  // Nur GF werden umgeleitet; andere Rollen sehen den Wizard nie.
  if (!istGF) return <>{children}</>;

  // Bereits auf der Wizard-Seite → nicht erneut umleiten (Loop vermeiden).
  if (location.pathname.startsWith("/onboarding-wizard"))
    return <>{children}</>;

  // Status noch nicht da → Inhalt schon zeigen (kein Blockieren des Cockpits).
  if (isLoading || !data) return <>{children}</>;

  if (data.wizard_durchlaufen === false) {
    return <Navigate to="/onboarding-wizard" replace />;
  }

  return <>{children}</>;
}
