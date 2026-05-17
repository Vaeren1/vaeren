import { ProtectedRoute } from "@/components/auth/protected-route";
import { SidebarShell } from "@/components/layout/sidebar-shell";
import { AuditExportDashboard } from "@/routes/audit-export";
import { AuditExportRunDetailPage } from "@/routes/audit-export-run-detail";
import { AuditExportWizardPage } from "@/routes/audit-export-wizard";
import { AuditLogPage } from "@/routes/audit-log";
import { VerifyPage } from "@/routes/verify";
import { AVVListPage } from "@/routes/auftragsverarbeitung";
import { DashboardPage } from "@/routes/dashboard";
import { DatenpanneDetailPage } from "@/routes/datenpanne-detail";
import { DatenpanneFormPage } from "@/routes/datenpanne-form";
import { DatenpannenListPage } from "@/routes/datenpannen";
import { DemoPage } from "@/routes/demo";
import { KIInventarListPage } from "@/routes/ki-inventar";
import { KIToolDetailPage } from "@/routes/ki-tool-detail";
import { KIToolFormPage } from "@/routes/ki-tool-form";
import { NIS2Page } from "@/routes/nis2";
import { KursDetailPage } from "@/routes/kurs-detail";
import { KursFormPage } from "@/routes/kurs-form";
import { KurseListPage } from "@/routes/kurse";
import { LoginPage } from "@/routes/login";
import { MeldungDetailPage } from "@/routes/meldung-detail";
import { MeldungenListPage } from "@/routes/meldungen";
import { MfaChallengePage } from "@/routes/mfa-challenge";
import { MfaSetupPage } from "@/routes/mfa-setup";
import { MitarbeiterListPage } from "@/routes/mitarbeiter";
import { MitarbeiterFormPage } from "@/routes/mitarbeiter-form";
import { OnboardingSetupPage } from "@/routes/onboarding-setup";
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
  { path: "/onboarding/setup", element: <OnboardingSetupPage /> },
  { path: "/verify", element: <VerifyPage /> },
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
      { path: "/kurse/neu", element: <KursFormPage /> },
      { path: "/kurse/:id", element: <KursDetailPage /> },
      { path: "/kurse/:id/bearbeiten", element: <KursFormPage /> },
      { path: "/meldungen", element: <MeldungenListPage /> },
      { path: "/meldungen/:id", element: <MeldungDetailPage /> },
      { path: "/audit", element: <AuditLogPage /> },
      { path: "/audit-export", element: <AuditExportDashboard /> },
      { path: "/audit-export/profil/neu", element: <AuditExportWizardPage /> },
      { path: "/audit-export/runs/:id", element: <AuditExportRunDetailPage /> },
      { path: "/datenpannen", element: <DatenpannenListPage /> },
      { path: "/datenpannen/neu", element: <DatenpanneFormPage /> },
      { path: "/datenpannen/:id", element: <DatenpanneDetailPage /> },
      { path: "/ki-inventar", element: <KIInventarListPage /> },
      { path: "/ki-inventar/neu", element: <KIToolFormPage /> },
      { path: "/ki-inventar/:id", element: <KIToolDetailPage /> },
      { path: "/avv", element: <AVVListPage /> },
      { path: "/nis2", element: <NIS2Page /> },
      { path: "/redaktion", element: <RedaktionPage /> },
      { path: "/settings", element: <SettingsPage /> },
      { path: "/mfa-setup", element: <MfaSetupPage /> },
    ],
  },
]);
