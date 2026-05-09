/**
 * Audit-Log-Viewer (Stripe-Style).
 * Filter-Chips oben, Tabelle mit Click-to-expand für JSON-Diff,
 * CSV-Download in Header.
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
import {
  type AuditEntry,
  buildAuditCsvUrl,
  useAuditList,
} from "@/lib/api/audit";
import { cn } from "@/lib/utils";
import { Download, FileSearch } from "lucide-react";
import { useState } from "react";

const AKTION_OPTIONS = [
  { v: "", label: "alle" },
  { v: "create", label: "Erstellt" },
  { v: "update", label: "Aktualisiert" },
  { v: "delete", label: "Gelöscht" },
  { v: "login", label: "Login" },
  { v: "logout", label: "Logout" },
  { v: "export", label: "Export" },
];

export function AuditLogPage() {
  const [aktion, setAktion] = useState<string>("");
  const [from, setFrom] = useState<string>("");
  const [to, setTo] = useState<string>("");
  const [expanded, setExpanded] = useState<number | null>(null);

  const filters = {
    aktion: aktion || undefined,
    from: from || undefined,
    to: to || undefined,
  };
  const { data, isLoading, isError } = useAuditList(filters);

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between">
        <div>
          <CardTitle>Audit-Log</CardTitle>
          <CardDescription>
            Vollständiger, manipulationssicherer Audit-Trail (DSGVO Art. 32, ISO
            27001 A.12.4). Zugriff: GF + IT-Leiter.
          </CardDescription>
        </div>
        <Button asChild variant="outline" size="sm">
          <a href={buildAuditCsvUrl(filters)}>
            <Download size={14} className="mr-1" /> CSV exportieren
          </a>
        </Button>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-wrap items-end gap-3 rounded border bg-slate-50 p-3">
          <div className="flex flex-col gap-1">
            <Label className="text-xs">Aktion</Label>
            <select
              value={aktion}
              onChange={(e) => setAktion(e.target.value)}
              className="rounded border bg-white px-2 py-1.5 text-sm"
            >
              {AKTION_OPTIONS.map((o) => (
                <option key={o.v} value={o.v}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <Label className="text-xs">Von</Label>
            <Input
              type="date"
              value={from}
              onChange={(e) => setFrom(e.target.value)}
              className="w-40"
            />
          </div>
          <div className="flex flex-col gap-1">
            <Label className="text-xs">Bis</Label>
            <Input
              type="date"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              className="w-40"
            />
          </div>
          {(aktion || from || to) && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setAktion("");
                setFrom("");
                setTo("");
              }}
            >
              Filter zurücksetzen
            </Button>
          )}
        </div>

        {isError && (
          <p className="text-sm text-rose-700">
            Keine Berechtigung oder Fehler beim Laden.
          </p>
        )}
        {isLoading && (
          <div className="space-y-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div
                key={i}
                className="h-10 animate-pulse rounded bg-slate-100"
              />
            ))}
          </div>
        )}
        {data && data.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <FileSearch size={28} className="text-slate-400" />
            <p className="mt-2 text-sm font-medium">Keine Einträge gefunden.</p>
            <p className="text-xs text-slate-500">
              Andere Filter wählen oder Filter zurücksetzen.
            </p>
          </div>
        )}
        {data && data.length > 0 && (
          <div className="overflow-hidden rounded-md border">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-3 py-2">Zeitpunkt</th>
                  <th className="px-3 py-2">Aktor</th>
                  <th className="px-3 py-2">Aktion</th>
                  <th className="px-3 py-2">Ziel</th>
                  <th className="px-3 py-2">IP</th>
                </tr>
              </thead>
              <tbody>
                {data.map((entry) => (
                  <AuditRow
                    key={entry.id}
                    entry={entry}
                    expanded={expanded === entry.id}
                    onToggle={() =>
                      setExpanded(expanded === entry.id ? null : entry.id)
                    }
                  />
                ))}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function AuditRow({
  entry,
  expanded,
  onToggle,
}: {
  entry: AuditEntry;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <>
      <tr
        onClick={onToggle}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            onToggle();
          }
        }}
        tabIndex={0}
        className={cn(
          "cursor-pointer border-t hover:bg-slate-50 focus:bg-slate-100 focus:outline-none",
          expanded && "bg-slate-50",
        )}
      >
        <td className="px-3 py-2 tabular-nums text-xs text-slate-600">
          {new Date(entry.timestamp).toLocaleString("de-DE")}
        </td>
        <td className="px-3 py-2">{entry.actor_email || "system"}</td>
        <td className="px-3 py-2">
          <span
            className={cn(
              "rounded px-2 py-0.5 text-xs font-medium",
              entry.aktion === "delete"
                ? "bg-rose-100 text-rose-800"
                : entry.aktion === "create"
                  ? "bg-emerald-100 text-emerald-800"
                  : entry.aktion === "update"
                    ? "bg-sky-100 text-sky-800"
                    : "bg-slate-100 text-slate-700",
            )}
          >
            {entry.aktion}
          </span>
        </td>
        <td className="px-3 py-2 text-xs text-slate-600">
          {entry.target_type ? (
            <>
              {entry.target_type}
              {entry.target_object_id ? ` #${entry.target_object_id}` : ""}
            </>
          ) : (
            "—"
          )}
        </td>
        <td className="px-3 py-2 font-mono text-xs text-slate-500">
          {entry.ip_address ?? "—"}
        </td>
      </tr>
      {expanded && (
        <tr className="border-t">
          <td colSpan={5} className="bg-slate-900 p-3">
            <pre className="overflow-x-auto text-xs text-emerald-200">
              {JSON.stringify(entry.aenderung_diff, null, 2)}
            </pre>
          </td>
        </tr>
      )}
    </>
  );
}
