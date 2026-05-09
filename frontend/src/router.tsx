import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { AppShell } from "@/components/layout/app-shell";
import { DemoPage } from "@/routes/demo";
import { LoginPage } from "@/routes/login";
import { MfaChallengePage } from "@/routes/mfa-challenge";
import { MfaSetupPage } from "@/routes/mfa-setup";
import { MitarbeiterFormPage } from "@/routes/mitarbeiter-form";
import { MitarbeiterListPage } from "@/routes/mitarbeiter";

export const router = createBrowserRouter([
  { path: "/login", element: <LoginPage /> },
  { path: "/mfa-challenge", element: <MfaChallengePage /> },
  { path: "/demo", element: <DemoPage /> },
  {
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      { path: "/", element: <Navigate to="/mitarbeiter" replace /> },
      { path: "/mitarbeiter", element: <MitarbeiterListPage /> },
      { path: "/mitarbeiter/neu", element: <MitarbeiterFormPage /> },
      {
        path: "/mitarbeiter/:id/bearbeiten",
        element: <MitarbeiterFormPage />,
      },
      { path: "/mfa-setup", element: <MfaSetupPage /> },
    ],
  },
]);
