/**
 * Run-Detail mit Generation-Log + Download-Buttons.
 *
 * Polling alle 5 s solange status=running/queued.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  downloadUrls,
  getRun,
  type AuditExportRunDetail,
  type RunStatus,
} from "@/lib/api/audit_export";
import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

function StatusBadge({ status }: { status: RunStatus }) {
  const STYLES: Record<RunStatus, string> = {
    queued: "bg-slate-100 text-slate-700",
    running: "bg-amber-100 text-amber-800",
    done: "bg-emerald-100 text-emerald-800",
    failed: "bg-rose-100 text-rose-800",
    cancelled: "bg-slate-200 text-slate-600",
  };
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}
    >
      {status}
    </span>
  );
}

function logRowStyle(level: string): string {
  if (level === "error") return "text-rose-700";
  if (level === "warning") return "text-amber-700";
  return "text-slate-700";
}

export function AuditExportRunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const runId = Number(id);

  const run = useQuery({
    queryKey: ["audit-export", "run", runId],
    queryFn: () => getRun(runId),
    enabled: !Number.isNaN(runId),
    refetchInterval: (q) => {
      const status = q.state.data?.status;
      if (status === "running" || status === "queued") return 5000;
      return false;
    },
  });

  if (run.isLoading) return <p>Lade …</p>;
  if (run.isError || !run.data)
    return <p className="text-destructive">Run nicht gefunden.</p>;

  const r: AuditExportRunDetail = run.data;
  const urls = downloadUrls(r.id);
  const verifyUrl = `${window.location.origin}/verify?mappe=${encodeURIComponent(
    r.mappe_id,
  )}&hash=${encodeURIComponent(r.file_hash_sha256)}`;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="font-mono">{r.mappe_id}</CardTitle>
            <StatusBadge status={r.status} />
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm">
            <dt className="text-muted-foreground">Gestartet</dt>
            <dd>{new Date(r.started_at).toLocaleString("de-DE")}</dd>

            <dt className="text-muted-foreground">Beendet</dt>
            <dd>
              {r.finished_at
                ? new Date(r.finished_at).toLocaleString("de-DE")
                : "—"}
            </dd>

            <dt className="text-muted-foreground">Belege gesamt</dt>
            <dd>{r.evidence_count}</dd>

            <dt className="text-muted-foreground">Bundle-Größe</dt>
            <dd>{(r.file_size_bytes / 1024).toFixed(1)} KB</dd>

            <dt className="text-muted-foreground">Bundle SHA-256</dt>
            <dd className="font-mono text-xs break-all">
              {r.file_hash_sha256 || "(noch nicht berechnet)"}
            </dd>

            <dt className="text-muted-foreground">PDF SHA-256</dt>
            <dd className="font-mono text-xs break-all">
              {r.pdf_hash_sha256 || "(noch nicht berechnet)"}
            </dd>
          </dl>

          {r.error && (
            <p className="text-destructive text-sm">
              <strong>Fehler:</strong> {r.error}
            </p>
          )}

          {r.status === "done" && (
            <>
              <div className="flex flex-wrap gap-2 border-t pt-3">
                <Button asChild>
                  <a href={urls.zip}>Bundle (ZIP)</a>
                </Button>
                <Button asChild variant="outline">
                  <a href={urls.pdf}>PDF-Mappe</a>
                </Button>
                <Button asChild variant="outline">
                  <a href={urls.oscalSsp}>OSCAL SSP</a>
                </Button>
                <Button asChild variant="outline">
                  <a href={urls.oscalAssessment}>OSCAL AR</a>
                </Button>
              </div>

              <div className="border-t pt-3 space-y-2">
                <h3 className="text-sm font-semibold">Verify-Link</h3>
                <input
                  type="text"
                  readOnly
                  value={verifyUrl}
                  onClick={(e) => (e.target as HTMLInputElement).select()}
                  className="w-full rounded border px-2 py-1 text-xs font-mono bg-muted"
                />
                <p className="text-xs text-muted-foreground">
                  Diesen Link an Auditor:innen geben — sie können damit die
                  Authentizität der Mappe gegen Vaeren prüfen.
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Generation-Log</CardTitle>
        </CardHeader>
        <CardContent>
          {r.generation_log.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Noch keine Log-Einträge.
            </p>
          )}
          <ul className="space-y-1 font-mono text-xs">
            {r.generation_log.map((entry, i) => (
              <li key={i} className={logRowStyle(entry.level)}>
                <span className="text-muted-foreground">
                  {new Date(entry.ts).toLocaleTimeString("de-DE")}
                </span>{" "}
                <strong>[{entry.aggregator}]</strong> {entry.message}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
