import { ProtectedRoute } from "@/components/auth/protected-route";
import { SidebarShell } from "@/components/layout/sidebar-shell";
import { AuditLogPage } from "@/routes/audit-log";
import { DashboardPage } from "@/routes/dashboard";
import { DemoPage } from "@/routes/demo";
import { KursDetailPage } from "@/routes/kurs-detail";
import { KurseListPage } from "@/routes/kurse";
import { LoginPage } from "@/routes/login";
import { MeldungDetailPage } from "@/routes/meldung-detail";
import { MeldungenListPage } from "@/routes/meldungen";
import { MfaChallengePage } from "@/routes/mfa-challenge";
import { MfaSetupPage } from "@/routes/mfa-setup";
import { MitarbeiterListPage } from "@/routes/mitarbeiter";
import { MitarbeiterFormPage } from "@/routes/mitarbeiter-form";
import { PublicHinweisePage } from "@/routes/public-hinweise";
import { PublicHinweiseStatusPage } from "@/routes/public-hinweise-status";
import { PublicSchulungPage } from "@/routes/public-schulung";
import { RedaktionPage } from "@/routes/redaktion";
import { SchulungenListPage } from "@/routes/schulungen";
import { SchulungenWizardPage } from "@/routes/schulungen-wizard";
import { SettingsPage } from "@/routes/settings";
import { WelleDetailPage } from "@/routes/welle-detail";
import { createBrowserRouter } from "react-router-dom";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/mfa-challenge", element: <MfaChallengePage /> },
  { path: "/demo", element: <DemoPage /> },
  { path: "/schulung/:token", element: <PublicSchulungPage /> },
  { path: "/hinweise", element: <PublicHinweisePage /> },
  { path: "/hinweise/status/:token", element: <PublicHinweiseStatusPage /> },
  {
    element: (
      <ProtectedRoute>
        <SidebarShell />
      </ProtectedRoute>
    ),
    children: [
      { path: "/", element: <DashboardPage /> },
      { path: "/mitarbeiter", element: <MitarbeiterListPage /> },
      { path: "/mitarbeiter/neu", element: <MitarbeiterFormPage /> },
      {
        path: "/mitarbeiter/:id/bearbeiten",
        element: <MitarbeiterFormPage />,
      },
      { path: "/schulungen", element: <SchulungenListPage /> },
      { path: "/schulungen/neu", element: <SchulungenWizardPage /> },
      { path: "/schulungen/:id", element: <WelleDetailPage /> },
      { path: "/kurse", element: <KurseListPage /> },
      { path: "/kurse/:id", element: <KursDetailPage /> },
      { path: "/meldungen", element: <MeldungenListPage /> },
      { path: "/meldungen/:id", element: <MeldungDetailPage /> },
      { path: "/audit", element: <AuditLogPage /> },
      { path: "/redaktion", element: <RedaktionPage /> },
      { path: "/settings", element: <SettingsPage /> },
      { path: "/mfa-setup", element: <MfaSetupPage /> },
    ],
  },
]);
