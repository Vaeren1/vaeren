/**
 * Audit-Export-Dashboard.
 *
 * Linke Spalte: Profile-Liste (Wizard-Einstieg, Run-Trigger).
 * Rechte Spalte: Run-History (letzte 30 Tage), Status-Badges, Download.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  downloadUrls,
  listProfiles,
  listRuns,
  startRun,
  TEMPLATE_LABEL,
  type AuditExportProfile,
  type AuditExportRunListItem,
  type RunStatus,
} from "@/lib/api/audit_export";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link } from "react-router-dom";

function StatusBadge({ status }: { status: RunStatus }) {
  const STYLES: Record<RunStatus, string> = {
    queued: "bg-slate-100 text-slate-700",
    running: "bg-amber-100 text-amber-800",
    done: "bg-emerald-100 text-emerald-800",
    failed: "bg-rose-100 text-rose-800",
    cancelled: "bg-slate-200 text-slate-600",
  };
  const LABEL: Record<RunStatus, string> = {
    queued: "Eingereiht",
    running: "Läuft",
    done: "Fertig",
    failed: "Fehlgeschlagen",
    cancelled: "Abgebrochen",
  };
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}
    >
      {LABEL[status]}
    </span>
  );
}

function formatBytes(b: number): string {
  if (b < 1024) return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1024 / 1024).toFixed(1)} MB`;
}

export function AuditExportDashboard() {
  const qc = useQueryClient();
  const profiles = useQuery({
    queryKey: ["audit-export", "profiles"],
    queryFn: listProfiles,
  });
  const runs = useQuery({
    queryKey: ["audit-export", "runs"],
    queryFn: listRuns,
    refetchInterval: (q) => {
      const hasRunning = q.state.data?.results?.some(
        (r: AuditExportRunListItem) =>
          r.status === "running" || r.status === "queued",
      );
      return hasRunning ? 5000 : false;
    },
  });

  const startRunMut = useMutation({
    mutationFn: (profileId: number) => startRun(profileId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["audit-export", "runs"] }),
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Audit-Export — Profile</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Wiederverwendbare Konfigurationen für Audit-Mappen. Eine Mappe enthält
              PDF, OSCAL-JSON und ZIP-Beweismappe mit HMAC-Signatur.
            </p>
          </div>
          <Button asChild>
            <Link to="/audit-export/profil/neu">+ Neues Profile</Link>
          </Button>
        </CardHeader>
        <CardContent>
          {profiles.isLoading && <p>Lade Profile …</p>}
          {profiles.isError && (
            <p className="text-destructive">Fehler beim Laden der Profile.</p>
          )}
          {profiles.data && profiles.data.results.length === 0 && (
            <p className="text-muted-foreground">
              Noch kein Profile angelegt.{" "}
              <Link to="/audit-export/profil/neu" className="underline">
                Erstes Profile anlegen
              </Link>
            </p>
          )}
          {profiles.data && profiles.data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Template</TableHead>
                  <TableHead>Zeitraum</TableHead>
                  <TableHead>Norm-Scope</TableHead>
                  <TableHead className="text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {profiles.data.results.map((p: AuditExportProfile) => (
                  <TableRow key={p.id}>
                    <TableCell>
                      <Link
                        to={`/audit-export/profil/${p.id}`}
                        className="font-medium underline"
                      >
                        {p.name}
                      </Link>
                    </TableCell>
                    <TableCell>{TEMPLATE_LABEL[p.template]}</TableCell>
                    <TableCell>
                      {p.zeitraum_von} – {p.zeitraum_bis}
                    </TableCell>
                    <TableCell>
                      <span className="text-xs text-muted-foreground">
                        {p.norm_scope.join(", ")}
                      </span>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        size="sm"
                        onClick={() => startRunMut.mutate(p.id)}
                        disabled={startRunMut.isPending}
                      >
                        Run starten
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Run-History</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Generierte Audit-Mappen. Aktualisiert sich automatisch bei laufenden
            Runs (Polling alle 5 s).
          </p>
        </CardHeader>
        <CardContent>
          {runs.isLoading && <p>Lade …</p>}
          {runs.data && runs.data.results.length === 0 && (
            <p className="text-muted-foreground">Noch keine Runs.</p>
          )}
          {runs.data && runs.data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Mappe-ID</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Gestartet</TableHead>
                  <TableHead>Belege</TableHead>
                  <TableHead>Größe</TableHead>
                  <TableHead className="text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {runs.data.results.map((r) => {
                  const urls = downloadUrls(r.id);
                  return (
                    <TableRow key={r.id}>
                      <TableCell className="font-mono text-xs">
                        <Link
                          to={`/audit-export/runs/${r.id}`}
                          className="underline"
                        >
                          {r.mappe_id}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <StatusBadge status={r.status} />
                      </TableCell>
                      <TableCell>
                        {new Date(r.started_at).toLocaleString("de-DE")}
                      </TableCell>
                      <TableCell>{r.evidence_count}</TableCell>
                      <TableCell>{formatBytes(r.file_size_bytes)}</TableCell>
                      <TableCell className="text-right space-x-2">
                        {r.status === "done" && (
                          <>
                            <Button asChild size="sm" variant="outline">
                              <a href={urls.zip}>ZIP</a>
                            </Button>
                            <Button asChild size="sm" variant="outline">
                              <a href={urls.pdf}>PDF</a>
                            </Button>
                          </>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
