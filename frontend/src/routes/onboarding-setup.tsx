/**
 * Onboarding-Setup-Seite. Wird auf `<schema>.app.vaeren.de/onboarding/setup?token=...`
 * vom Magic-Link aus aufgerufen.
 *
 * Flow:
 *  1. Mount: GET /api/onboarding/setup/?token=... → Info anzeigen (Email, Firma)
 *  2. User füllt Passwort-Form (2× Eingabe + Strength-Indikator)
 *  3. POST /api/onboarding/setup/ {token, new_password} → 200 = User logged in
 *     → redirect zum Dashboard
 *
 * Kein ProtectedRoute-Wrapper — diese Seite wird *vor* dem Login aufgerufen.
 */

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

interface SetupInfo {
  firma_name: string;
  vorname: string;
  email: string;
  status: string;
  schema_name: string;
  expires_at: string | null;
}

interface SetupError {
  detail: string;
  code: string;
}

const PASSWORD_MIN_LEN = 12;

function passwordStrength(pw: string): {
  label: string;
  color: string;
  score: number;
} {
  let score = 0;
  if (pw.length >= 12) score++;
  if (pw.length >= 16) score++;
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++;
  if (/\d/.test(pw)) score++;
  if (/[^a-zA-Z0-9]/.test(pw)) score++;
  const labels = [
    { label: "Sehr schwach", color: "text-red-600" },
    { label: "Schwach", color: "text-red-600" },
    { label: "Mäßig", color: "text-amber-600" },
    { label: "Gut", color: "text-amber-600" },
    { label: "Stark", color: "text-emerald-600" },
    { label: "Sehr stark", color: "text-emerald-600" },
  ];
  return { ...labels[Math.min(score, 5)], score };
}

export function OnboardingSetupPage() {
  const [params] = useSearchParams();
  const token = params.get("token") ?? "";
  const navigate = useNavigate();

  const [info, setInfo] = useState<SetupInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<SetupError | null>(null);

  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const strength = useMemo(() => passwordStrength(password), [password]);
  const passwordsMatch = password === password2 && password.length > 0;
  const canSubmit =
    !submitting && password.length >= PASSWORD_MIN_LEN && passwordsMatch;

  useEffect(() => {
    if (!token) {
      setLoadError({
        detail: "Aktivierungs-Link ist unvollständig (Token fehlt).",
        code: "token_required",
      });
      setLoading(false);
      return;
    }
    fetch(`/api/onboarding/setup/?token=${encodeURIComponent(token)}`, {
      credentials: "include",
    })
      .then(async (res) => {
        if (res.ok) {
          setInfo((await res.json()) as SetupInfo);
        } else {
          const body = (await res.json().catch(() => null)) as SetupError | null;
          setLoadError(
            body ?? {
              detail: "Aktivierungs-Link konnte nicht geprüft werden.",
              code: "load_error",
            },
          );
        }
      })
      .catch(() =>
        setLoadError({ detail: "Netzwerkfehler. Bitte erneut versuchen.", code: "network" }),
      )
      .finally(() => setLoading(false));
  }, [token]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitError(null);
    if (!canSubmit) return;
    setSubmitting(true);
    try {
      const res = await fetch("/api/onboarding/setup/", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });
      if (res.status === 200) {
        // User ist via login()-Aufruf eingeloggt. Direkt zum Dashboard.
        navigate("/", { replace: true });
        return;
      }
      const body = (await res.json().catch(() => null)) as SetupError | null;
      setSubmitError(body?.detail ?? "Aktivierung fehlgeschlagen. Bitte erneut versuchen.");
    } catch {
      setSubmitError("Netzwerkfehler. Bitte erneut versuchen.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto max-w-md py-16">
        <Card>
          <CardHeader>
            <CardTitle>Aktivierung wird geladen …</CardTitle>
          </CardHeader>
        </Card>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="container mx-auto max-w-md py-16">
        <Card>
          <CardHeader>
            <CardTitle>Aktivierungs-Link ungültig</CardTitle>
            <CardDescription>{loadError.detail}</CardDescription>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground">
            <p>
              Falls Sie der Meinung sind, dass das ein Fehler ist, schreiben Sie
              bitte an <a className="underline" href="mailto:kontakt@vaeren.de">kontakt@vaeren.de</a>.
              Halten Sie den Link aus der E-Mail bereit.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!info) return null;

  if (info.status === "activated") {
    return (
      <div className="container mx-auto max-w-md py-16">
        <Card>
          <CardHeader>
            <CardTitle>Bereits aktiviert</CardTitle>
            <CardDescription>
              Dieser Account wurde bereits eingerichtet. Bitte direkt einloggen.
            </CardDescription>
          </CardHeader>
          <CardFooter>
            <Button onClick={() => navigate("/login")}>Zum Login</Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-md py-12">
      <Card>
        <CardHeader>
          <CardTitle>Willkommen bei Vaeren, {info.vorname}.</CardTitle>
          <CardDescription>
            Sie sind dabei, den Mandanten <strong>{info.firma_name}</strong> einzurichten.
            Bitte legen Sie ein Passwort für <strong>{info.email}</strong> fest.
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">Passwort (mindestens 12 Zeichen)</Label>
              <Input
                id="password"
                type="password"
                autoComplete="new-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={PASSWORD_MIN_LEN}
              />
              {password.length > 0 && (
                <p className={`text-xs ${strength.color}`}>
                  Stärke: {strength.label}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="password2">Passwort wiederholen</Label>
              <Input
                id="password2"
                type="password"
                autoComplete="new-password"
                value={password2}
                onChange={(e) => setPassword2(e.target.value)}
                required
              />
              {password2.length > 0 && !passwordsMatch && (
                <p className="text-xs text-red-600">Passwörter stimmen nicht überein.</p>
              )}
            </div>
            {submitError && (
              <p className="text-sm text-red-600" role="alert">{submitError}</p>
            )}
            <div className="rounded border border-amber-300 bg-amber-50 p-3 text-xs text-amber-900">
              <p className="font-semibold">Empfehlung</p>
              <p>
                Aktivieren Sie nach dem Login die Zwei-Faktor-Authentifizierung
                (Einstellungen → Sicherheit). Für die DSGVO-Konformität
                Ihres Accounts wird das in der nächsten Audit-Stufe Pflicht.
              </p>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col items-stretch space-y-2">
            <Button type="submit" disabled={!canSubmit}>
              {submitting ? "Account wird aktiviert …" : "Passwort speichern & loslegen"}
            </Button>
            <p className="text-xs text-muted-foreground text-center">
              30-Tage-Trial · keine Auto-Verlängerung · jederzeit per Mail kündbar
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
