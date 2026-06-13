/**
 * ISO-27001-Dashboard.
 *
 * Zeigt:
 * - Coverage-Donut (5 Status-Segmente) mit "X / 93" im Mittelpunkt
 * - Auditor-Readiness-Score (0-100) mit Komponenten-Tooltip
 * - Top-5-Risiken
 * - Kategorie-Verteilung
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getIsoDashboard } from "@/lib/api/iso27001";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

const STATUS_BG: Record<string, string> = {
  verifiziert: "bg-emerald-500",
  umgesetzt: "bg-blue-500",
  geplant: "bg-amber-500",
  nicht_bewertet: "bg-slate-300",
  nicht_anwendbar: "bg-white border border-slate-300",
};

const STATUS_LABEL: Record<string, string> = {
  verifiziert: "Verifiziert",
  umgesetzt: "Umgesetzt",
  geplant: "Geplant",
  nicht_bewertet: "Nicht bewertet",
  nicht_anwendbar: "Nicht anwendbar",
};

// Tailwind JIT erkennt KEINE dynamisch zusammengesetzten Klassen (`bg-${x}-500`).
// Wir mappen statisch, damit die Klassen im final-CSS landen.
const LEVEL_DOT_BG: Record<string, string> = {
  green: "bg-emerald-500",
  yellow: "bg-amber-500",
  red: "bg-rose-500",
};

export function Iso27001Dashboard() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["iso27001-dashboard"],
    queryFn: getIsoDashboard,
  });

  if (isError) {
    return (
      <p className="text-destructive">
        ISO-27001-Dashboard konnte nicht geladen werden. Bitte Seite neu laden.
      </p>
    );
  }
  if (isLoading || !data) {
    return <p>Lade ISO-27001-Dashboard …</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">ISO 27001</h1>
        <p className="text-sm text-muted-foreground">
          Annex-A-2022 Evidence-Sammler. Vom Tenant verantwortet — Vaeren
          liefert das Erfassungs-Werkzeug, KEIN Audit-Ergebnis.
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Coverage</CardTitle>
            <p className="text-xs text-muted-foreground">
              {data.coverage.verifiziert + data.coverage.umgesetzt} von{" "}
              {data.coverage.total - data.coverage.nicht_anwendbar} anwendbaren
              Controls umgesetzt.
            </p>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {(
                [
                  "verifiziert",
                  "umgesetzt",
                  "geplant",
                  "nicht_bewertet",
                  "nicht_anwendbar",
                ] as const
              ).map((status) => (
                <div key={status} className="flex items-center gap-2 text-sm">
                  <span
                    className={`inline-block h-3 w-3 rounded ${STATUS_BG[status]}`}
                  />
                  <span className="flex-1">{STATUS_LABEL[status]}</span>
                  <span className="font-mono">
                    {data.coverage[status]} / {data.coverage.total}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Auditor-Readiness</CardTitle>
            <p className="text-xs text-muted-foreground">
              {data.readiness.detail}
            </p>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold">{data.readiness.total}</span>
              <span className="text-sm text-muted-foreground">/ 100</span>
            </div>
            <ul className="mt-3 space-y-1 text-xs text-muted-foreground">
              <li>Coverage: {data.readiness.coverage}%</li>
              <li>Risiken behandelt: {data.readiness.risiken}%</li>
              <li>Audit-Aktualität: {data.readiness.audit_aktualitaet}%</li>
              <li>
                Mgt-Review-Aktualität: {data.readiness.mgt_review_aktualitaet}%
              </li>
              <li>Evidence-Coverage: {data.readiness.evidence_coverage}%</li>
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Module-Score</CardTitle>
            <p className="text-xs text-muted-foreground">
              Beitrag zum Master-Compliance-Index.
            </p>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold">{data.module_score}</span>
              <span className="text-sm text-muted-foreground">/ 100</span>
              <span
                className={`ml-2 inline-block h-3 w-3 rounded-full ${LEVEL_DOT_BG[data.module_level] ?? "bg-slate-300"}`}
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top-Risiken</CardTitle>
        </CardHeader>
        <CardContent>
          {data.top_risiken.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Noch keine Risiken im Register.{" "}
              <Link to="/iso27001/risiken" className="underline">
                Erstes Risiko anlegen
              </Link>
              .
            </p>
          ) : (
            <ul className="space-y-2">
              {data.top_risiken.map((r) => (
                <li
                  key={r.id}
                  className="flex items-center justify-between text-sm border-b pb-1"
                >
                  <span>{r.titel}</span>
                  <span className="font-mono text-xs">
                    Score {r.risk_score_brutto} · {r.treatment}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-2">
        <Button asChild>
          <Link to="/iso27001/controls">93 Controls verwalten</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/iso27001/risiken">Risiko-Register</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/iso27001/soa">SoA generieren</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/iso27001/audits">Audits & Findings</Link>
        </Button>
        <Button asChild variant="outline">
          <Link to="/iso27001/management-review">Management-Review</Link>
        </Button>
      </div>
    </div>
  );
}
