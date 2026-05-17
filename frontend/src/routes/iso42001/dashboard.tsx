/**
 * ISO-42001-Dashboard: Coverage-Donut + KPIs + ToDos-Vorschau.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getDashboard } from "@/lib/api/iso42001";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

function ProgressBar({ value, label }: { value: number; label: string }) {
  const pct = Math.round(value * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span>{label}</span>
        <span className="font-semibold">{pct}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-emerald-500"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function Iso42001DashboardPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["iso42001-dashboard"],
    queryFn: getDashboard,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">ISO 42001 — KI-Management-System</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Modul-Status, Score-Beitrag und Sub-Metriken. AIMS-Geltungsbereich und
          Lifecycle-Pflichten nach ISO/IEC 42001:2023.
        </p>
      </div>

      {isLoading && <p>Lade …</p>}
      {isError && (
        <p className="text-destructive">
          Modul nicht aktiv oder Fehler beim Laden. Aktivierung in den{" "}
          <Link to="/settings" className="underline">
            Einstellungen
          </Link>{" "}
          (Geschäftsführung).
        </p>
      )}

      {data && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Score-Beitrag</CardTitle>
                <p className="text-xs text-muted-foreground">
                  Der ISO-42001-Beitrag zum Compliance-Index (max{" "}
                  {data.score.gesamt_punkte_max} von 100 Punkten).
                </p>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="text-3xl font-semibold">
                  {data.score.gesamt_punkte.toFixed(1)} /{" "}
                  {data.score.gesamt_punkte_max}
                </div>
                <ProgressBar value={data.score.controls_anteil} label="Controls umgesetzt" />
                <ProgressBar value={data.score.aiia_anteil} label="AIIAs für Hoch-Risiko-Systeme" />
                <ProgressBar value={data.score.policies_anteil} label="Aktive Policies" />
                <ProgressBar value={data.score.incident_disziplin} label="Incident-Disziplin" />
                <ProgressBar value={data.score.review_aktuell} label="Management-Review aktuell" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Kennzahlen</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex justify-between border-b py-1">
                    <span>Controls umgesetzt</span>
                    <span className="font-semibold">
                      {data.kpis.controls_umgesetzt} / {data.kpis.controls_total}
                    </span>
                  </li>
                  <li className="flex justify-between border-b py-1">
                    <span>AI-Systeme im AIMS-Scope</span>
                    <span className="font-semibold">{data.kpis.ai_systems_in_scope}</span>
                  </li>
                  <li className="flex justify-between border-b py-1">
                    <span>AIIAs freigegeben</span>
                    <span className="font-semibold">{data.kpis.aiias_freigegeben}</span>
                  </li>
                  <li className="flex justify-between border-b py-1">
                    <span>Aktive Policies</span>
                    <span className="font-semibold">{data.kpis.policies_aktiv}</span>
                  </li>
                  <li className="flex justify-between border-b py-1">
                    <span>Offene Incidents</span>
                    <span className="font-semibold">{data.kpis.incidents_offen}</span>
                  </li>
                  <li className="flex justify-between py-1">
                    <span>Letzte Management-Review</span>
                    <span className="font-semibold">
                      {data.kpis.management_review_letzte ?? "—"}
                    </span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Schnellaktionen</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-wrap gap-2">
              <Link to="/iso42001/controls" className="rounded border px-3 py-2 text-sm hover:bg-slate-50">
                Statement of Applicability
              </Link>
              <Link to="/iso42001/policies" className="rounded border px-3 py-2 text-sm hover:bg-slate-50">
                KI-Policies
              </Link>
              <Link to="/iso42001/ki-systeme" className="rounded border px-3 py-2 text-sm hover:bg-slate-50">
                AI-Systeme
              </Link>
              <Link to="/iso42001/aiias" className="rounded border px-3 py-2 text-sm hover:bg-slate-50">
                AIIAs
              </Link>
              <Link to="/iso42001/incidents" className="rounded border px-3 py-2 text-sm hover:bg-slate-50">
                KI-Vorfälle
              </Link>
              <Link to="/iso42001/management-review" className="rounded border px-3 py-2 text-sm hover:bg-slate-50">
                Management-Review
              </Link>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
