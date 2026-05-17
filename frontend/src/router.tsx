import { ProtectedRoute } from "@/components/auth/protected-route";
import { SidebarShell } from "@/components/layout/sidebar-shell";
import { AuditLogPage } from "@/routes/audit-log";
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
import { lazy, Suspense } from "react";

const ArbeitsschutzDashboardPage = lazy(() =>
  import("@/routes/arbeitsschutz/Dashboard").then((m) => ({
    default: m.ArbeitsschutzDashboardPage,
  })),
);
const StrukturPage = lazy(() =>
  import("@/routes/arbeitsschutz/Struktur").then((m) => ({ default: m.StrukturPage })),
);
const GbuListPage = lazy(() =>
  import("@/routes/arbeitsschutz/GbuList").then((m) => ({ default: m.GbuListPage })),
);
const MassnahmenBoardPage = lazy(() =>
  import("@/routes/arbeitsschutz/MassnahmenBoard").then((m) => ({
    default: m.MassnahmenBoardPage,
  })),
);
const AsaCalendarPage = lazy(() =>
  import("@/routes/arbeitsschutz/AsaCalendar").then((m) => ({ default: m.AsaCalendarPage })),
);
const UnfallListPage = lazy(() =>
  import("@/routes/arbeitsschutz/UnfallList").then((m) => ({ default: m.UnfallListPage })),
);
const BeauftragteRegisterPage = lazy(() =>
  import("@/routes/arbeitsschutz/BeauftragteRegister").then((m) => ({
    default: m.BeauftragteRegisterPage,
  })),
);
const BetriebsanweisungBibliothekPage = lazy(() =>
  import("@/routes/arbeitsschutz/BetriebsanweisungBibliothek").then((m) => ({
    default: m.BetriebsanweisungBibliothekPage,
  })),
);

function Lazy({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<p>Lade…</p>}>{children}</Suspense>;
}
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
      { path: "/datenpannen", element: <DatenpannenListPage /> },
      { path: "/datenpannen/neu", element: <DatenpanneFormPage /> },
      { path: "/datenpannen/:id", element: <DatenpanneDetailPage /> },
      { path: "/ki-inventar", element: <KIInventarListPage /> },
      { path: "/ki-inventar/neu", element: <KIToolFormPage /> },
      { path: "/ki-inventar/:id", element: <KIToolDetailPage /> },
      { path: "/avv", element: <AVVListPage /> },
      { path: "/nis2", element: <NIS2Page /> },
      { path: "/arbeitsschutz", element: <Lazy><ArbeitsschutzDashboardPage /></Lazy> },
      { path: "/arbeitsschutz/struktur", element: <Lazy><StrukturPage /></Lazy> },
      { path: "/arbeitsschutz/gbu", element: <Lazy><GbuListPage /></Lazy> },
      { path: "/arbeitsschutz/massnahmen", element: <Lazy><MassnahmenBoardPage /></Lazy> },
      { path: "/arbeitsschutz/asa", element: <Lazy><AsaCalendarPage /></Lazy> },
      { path: "/arbeitsschutz/unfaelle", element: <Lazy><UnfallListPage /></Lazy> },
      { path: "/arbeitsschutz/beauftragte", element: <Lazy><BeauftragteRegisterPage /></Lazy> },
      { path: "/arbeitsschutz/betriebsanweisungen", element: <Lazy><BetriebsanweisungBibliothekPage /></Lazy> },
      { path: "/redaktion", element: <RedaktionPage /> },
      { path: "/settings", element: <SettingsPage /> },
      { path: "/mfa-setup", element: <MfaSetupPage /> },
    ],
  },
]);
