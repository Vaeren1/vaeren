/**
 * Tenant- und User-Settings (Sprint 6).
 * Tab-Navigation: Allgemein / Sicherheit / Datenschutz.
 */

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useTenantSettings, useUpdateTenantSettings } from "@/lib/api/settings";
import { cn } from "@/lib/utils";
import { useEffect, useState } from "react";
import { toast } from "sonner";

type Tab = "allgemein" | "sicherheit" | "datenschutz";

export function SettingsPage() {
  const [tab, setTab] = useState<Tab>("allgemein");
  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Einstellungen</h1>
        <p className="mt-1 text-sm text-slate-500">
          Tenant-weite Konfiguration und Sicherheits-Optionen.
        </p>
      </div>
      <div className="flex border-b">
        {(
          [
            ["allgemein", "Allgemein"],
            ["sicherheit", "Sicherheit"],
            ["datenschutz", "Datenschutz"],
          ] as Array<[Tab, string]>
        ).map(([v, l]) => (
          <button
            type="button"
            key={v}
            onClick={() => setTab(v)}
            className={cn(
              "border-b-2 px-4 py-2 text-sm transition",
              tab === v
                ? "border-emerald-600 font-medium text-emerald-700"
                : "border-transparent text-slate-600 hover:text-slate-900",
            )}
          >
            {l}
          </button>
        ))}
      </div>
      {tab === "allgemein" && <GeneralTab />}
      {tab === "sicherheit" && <SecurityTab />}
      {tab === "datenschutz" && <PrivacyTab />}
    </div>
  );
}

function GeneralTab() {
  const settings = useTenantSettings();
  const update = useUpdateTenantSettings();
  const [firmaName, setFirmaName] = useState("");
  const [locale, setLocale] = useState("de-DE");

  useEffect(() => {
    if (settings.data) {
      setFirmaName(settings.data.firma_name);
      setLocale(settings.data.locale);
    }
  }, [settings.data]);

  if (!settings.data) {
    return <div className="h-32 animate-pulse rounded-lg bg-slate-100" />;
  }
  const data = settings.data;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Tenant-Stammdaten</CardTitle>
        <CardDescription>
          Schema: <span className="font-mono">{data.schema_name}</span> · Plan:
          <span className="ml-1 capitalize">{data.plan}</span>{" "}
          {data.pilot && (
            <span className="ml-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">
              Pilot
            </span>
          )}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            update.mutate(
              { firma_name: firmaName, locale },
              {
                onSuccess: () => toast.success("Tenant-Daten aktualisiert."),
                onError: (err) => {
                  if (err.status === 403) {
                    toast.error(
                      "Keine Berechtigung — nur Geschäftsführer:innen.",
                    );
                  } else {
                    toast.error("Aktualisierung fehlgeschlagen.");
                  }
                },
              },
            );
          }}
          className="grid max-w-lg gap-4"
        >
          <div className="space-y-1">
            <Label htmlFor="firma_name">Firmenname</Label>
            <Input
              id="firma_name"
              required
              value={firmaName}
              onChange={(e) => setFirmaName(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="locale">Sprache</Label>
            <select
              id="locale"
              value={locale}
              onChange={(e) => setLocale(e.target.value)}
              className="rounded border bg-background px-2 py-2 text-sm"
            >
              <option value="de-DE">Deutsch (Deutschland)</option>
              <option value="de-AT">Deutsch (Österreich)</option>
              <option value="de-CH">Deutsch (Schweiz)</option>
            </select>
          </div>
          <Button type="submit" disabled={update.isPending}>
            Speichern
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

function SecurityTab() {
  const settings = useTenantSettings();
  const update = useUpdateTenantSettings();
  if (!settings.data) {
    return <div className="h-32 animate-pulse rounded-lg bg-slate-100" />;
  }
  const data = settings.data;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Mehr-Faktor-Authentifizierung</CardTitle>
          <CardDescription>
            Erzwingt MFA-Einrichtung für alle Mitarbeitenden des Tenants.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <label className="flex cursor-pointer items-start gap-3">
            <input
              type="checkbox"
              checked={data.mfa_required}
              onChange={(e) =>
                update.mutate(
                  { mfa_required: e.target.checked },
                  {
                    onSuccess: () =>
                      toast.success(
                        e.target.checked
                          ? "MFA jetzt für alle erzwungen."
                          : "MFA-Pflicht entfernt.",
                      ),
                    onError: (err) =>
                      toast.error(
                        err.status === 403
                          ? "Keine Berechtigung — nur Geschäftsführer:innen."
                          : "Aktualisierung fehlgeschlagen.",
                      ),
                  },
                )
              }
              className="mt-0.5 h-4 w-4"
            />
            <div>
              <div className="text-sm font-medium">MFA verpflichtend</div>
              <div className="text-xs text-slate-500">
                Wer sich anmeldet, muss zuvor TOTP einrichten. Existing Sessions
                bleiben gültig.
              </div>
            </div>
          </label>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>Verschlüsselung</CardTitle>
          <CardDescription>
            HinSchG-Meldungen werden mit einem tenant-spezifischen Fernet-Key
            (AES-128-CBC + HMAC-SHA256) verschlüsselt — siehe Architektur-Spec
            §4.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-1 text-sm">
            <li>
              <span className="text-slate-500">Verschlüsselung at rest:</span>{" "}
              <span className="font-medium text-emerald-700">✓ aktiv</span>
            </li>
            <li>
              <span className="text-slate-500">Hosting:</span> Hetzner Helsinki
              (EU)
            </li>
            <li>
              <span className="text-slate-500">Backup:</span> Hetzner Storage
              Box (verschlüsselt, Off-Site)
            </li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}

function PrivacyTab() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Aufbewahrungsfristen</CardTitle>
          <CardDescription>
            Alle gesetzlich definierten Pflichten — automatisch erzwungen.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            <li className="flex justify-between border-b pb-2">
              <span>HinSchG-Meldungen</span>
              <span className="font-medium">3 Jahre nach Abschluss</span>
            </li>
            <li className="flex justify-between border-b pb-2">
              <span>Schulungs-Zertifikate</span>
              <span className="font-medium">10 Jahre</span>
            </li>
            <li className="flex justify-between">
              <span>Audit-Log-Einträge</span>
              <span className="font-medium">
                unbegrenzt (Manipulationsschutz)
              </span>
            </li>
          </ul>
        </CardContent>
      </Card>
      <Card>
        <CardHeader>
          <CardTitle>DSGVO-Auskunftsrecht</CardTitle>
          <CardDescription>
            Datenexporte und Löschanträge (Phase 2 — automatisierter
            Self-Service).
          </CardDescription>
        </CardHeader>
        <CardContent className="text-sm text-slate-500">
          Aktuell auf Anfrage über{" "}
          <a className="underline" href="mailto:datenschutz@vaeren.de">
            datenschutz@vaeren.de
          </a>
          .
        </CardContent>
      </Card>
    </div>
  );
}
