/**
 * Audit-Detail-Seite: Header + Status-Switch + Findings-Liste + Anlage.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  createFinding,
  getAudit,
  listControls,
  listFindings,
  updateAudit,
  updateFinding,
  type AuditFinding,
  type InternesAudit,
  type Iso27001ControlListItem,
} from "@/lib/api/iso27001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";

const SCHWERE_VALUES: AuditFinding["schweregrad"][] = [
  "klein",
  "gross",
  "kritisch",
];

const SCHWERE_LABELS: Record<AuditFinding["schweregrad"], string> = {
  klein: "Klein (Hinweis)",
  gross: "Groß (Major)",
  kritisch: "Kritisch",
};

function schwereBadge(s: AuditFinding["schweregrad"]): string {
  if (s === "kritisch") return "bg-rose-100 text-rose-800 border-rose-300";
  if (s === "gross") return "bg-amber-100 text-amber-800 border-amber-300";
  return "bg-slate-100 text-slate-700 border-slate-300";
}

export function Iso27001AuditDetail() {
  const params = useParams<{ id: string }>();
  const auditId = Number(params.id);
  const qc = useQueryClient();

  const { data: audit, isLoading } = useQuery({
    queryKey: ["iso27001-audit", auditId],
    queryFn: () => getAudit(auditId),
    enabled: !Number.isNaN(auditId),
  });
  const { data: findings } = useQuery({
    queryKey: ["iso27001-findings", auditId],
    queryFn: () => listFindings(auditId),
    enabled: !Number.isNaN(auditId),
  });
  const { data: controls } = useQuery({
    queryKey: ["iso27001-controls"],
    queryFn: () => listControls(),
  });

  const [showFindingForm, setShowFindingForm] = useState(false);
  const [erledigeFinding, setErledigeFinding] = useState<AuditFinding | null>(
    null,
  );

  const statusMut = useMutation({
    mutationFn: (status: InternesAudit["status"]) =>
      updateAudit(auditId, { status }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-audit", auditId] });
      qc.invalidateQueries({ queryKey: ["iso27001-audits"] });
      toast.success("Status aktualisiert.");
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Status-Wechsel fehlgeschlagen"),
  });

  const createFindingMut = useMutation({
    mutationFn: createFinding,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-findings", auditId] });
      qc.invalidateQueries({ queryKey: ["iso27001-audit", auditId] });
      qc.invalidateQueries({ queryKey: ["iso27001-audits"] });
      toast.success("Finding angelegt.");
      setShowFindingForm(false);
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Finding-Anlage fehlgeschlagen"),
  });

  const erledigeMut = useMutation({
    mutationFn: (vars: { id: number; payload: Partial<AuditFinding> }) =>
      updateFinding(vars.id, vars.payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-findings", auditId] });
      toast.success("Finding als erledigt markiert.");
      setErledigeFinding(null);
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Speichern fehlgeschlagen"),
  });

  if (isLoading || !audit) {
    return <p>Lade …</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <Link to="/iso27001/audits" className="text-sm underline">
          ← Audit-Liste
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>{audit.titel}</CardTitle>
              <p className="mt-1 text-sm text-muted-foreground">
                {audit.auditzeitraum_von} → {audit.auditzeitraum_bis} ·{" "}
                {audit.auditor} · Status: <strong>{audit.status}</strong>
              </p>
            </div>
            <div className="flex gap-2">
              {audit.status === "geplant" && (
                <Button
                  variant="outline"
                  onClick={() => statusMut.mutate("laufend")}
                  disabled={statusMut.isPending}
                >
                  Starten
                </Button>
              )}
              {audit.status === "laufend" && (
                <Button
                  variant="outline"
                  onClick={() => statusMut.mutate("abgeschlossen")}
                  disabled={statusMut.isPending}
                >
                  Abschließen
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-xs text-muted-foreground">
            Geprüfte Controls: {audit.geprueft_controls.length}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <CardTitle>Findings ({findings?.results.length ?? 0})</CardTitle>
            <Button onClick={() => setShowFindingForm(true)}>
              + Finding anlegen
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {!findings || findings.results.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Noch keine Findings.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Schwere</TableHead>
                  <TableHead>Beschreibung</TableHead>
                  <TableHead>Maßnahme</TableHead>
                  <TableHead>Geplant bis</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {findings.results.map((f) => (
                  <TableRow key={f.id}>
                    <TableCell>
                      <span
                        className={`inline-flex rounded border px-2 py-0.5 text-xs ${schwereBadge(f.schweregrad)}`}
                      >
                        {SCHWERE_LABELS[f.schweregrad]}
                      </span>
                    </TableCell>
                    <TableCell className="text-sm">
                      {f.beschreibung.slice(0, 120)}
                    </TableCell>
                    <TableCell className="text-sm">
                      {f.massnahme.slice(0, 80)}
                    </TableCell>
                    <TableCell className="text-xs">
                      {f.geplant_bis ?? "—"}
                    </TableCell>
                    <TableCell className="text-xs">
                      {f.erledigt_am ? (
                        <span className="text-emerald-700">
                          ✓ {f.erledigt_am}
                        </span>
                      ) : (
                        <span className="text-amber-700">offen</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {!f.erledigt_am && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setErledigeFinding(f)}
                        >
                          Erledigt
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {showFindingForm && (
        <FindingForm
          auditId={auditId}
          controls={controls?.results ?? []}
          onCancel={() => setShowFindingForm(false)}
          onSubmit={(payload) => createFindingMut.mutate(payload)}
          isPending={createFindingMut.isPending}
        />
      )}

      {erledigeFinding && (
        <ErledigtDialog
          finding={erledigeFinding}
          onCancel={() => setErledigeFinding(null)}
          onSubmit={(payload) =>
            erledigeMut.mutate({ id: erledigeFinding.id, payload })
          }
          isPending={erledigeMut.isPending}
        />
      )}
    </div>
  );
}

function FindingForm({
  auditId,
  controls,
  onCancel,
  onSubmit,
  isPending,
}: {
  auditId: number;
  controls: Iso27001ControlListItem[];
  onCancel: () => void;
  onSubmit: (payload: Partial<AuditFinding>) => void;
  isPending: boolean;
}) {
  const [titel, setTitel] = useState("");
  const [beschreibung, setBeschreibung] = useState("");
  const [massnahme, setMassnahme] = useState("");
  const [schwere, setSchwere] = useState<AuditFinding["schweregrad"]>("klein");
  const [controlId, setControlId] = useState<number | "">("");
  const [geplantBis, setGeplantBis] = useState<string>("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 overflow-y-auto py-8">
      <form
        className="w-[640px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            audit: auditId,
            schweregrad: schwere,
            beschreibung: titel ? `${titel}\n\n${beschreibung}` : beschreibung,
            massnahme,
            betroffenes_control: controlId === "" ? null : Number(controlId),
            geplant_bis: geplantBis || null,
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">Neues Finding</h2>
        <div className="space-y-3">
          <div>
            <Label>Titel</Label>
            <Input
              value={titel}
              onChange={(e) => setTitel(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Beschreibung</Label>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm"
              rows={3}
              value={beschreibung}
              onChange={(e) => setBeschreibung(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Schweregrad</Label>
              <select
                className="w-full rounded border px-3 py-2 text-sm"
                value={schwere}
                onChange={(e) =>
                  setSchwere(e.target.value as AuditFinding["schweregrad"])
                }
              >
                {SCHWERE_VALUES.map((s) => (
                  <option key={s} value={s}>
                    {SCHWERE_LABELS[s]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Geplant bis (optional)</Label>
              <Input
                type="date"
                value={geplantBis}
                onChange={(e) => setGeplantBis(e.target.value)}
              />
            </div>
          </div>
          <div>
            <Label>Control-Bezug (optional)</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={controlId}
              onChange={(e) =>
                setControlId(e.target.value ? Number(e.target.value) : "")
              }
            >
              <option value="">— kein Control —</option>
              {controls.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.code} — {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Maßnahme</Label>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm"
              rows={2}
              value={massnahme}
              onChange={(e) => setMassnahme(e.target.value)}
              placeholder="Was muss getan werden, um das Finding zu beheben?"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Anlegen
          </Button>
        </div>
      </form>
    </div>
  );
}

function ErledigtDialog({
  finding,
  onCancel,
  onSubmit,
  isPending,
}: {
  finding: AuditFinding;
  onCancel: () => void;
  onSubmit: (payload: Partial<AuditFinding>) => void;
  isPending: boolean;
}) {
  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 10));
  const [bemerkung, setBemerkung] = useState(
    finding.wirksamkeit_bemerkung ?? "",
  );

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[560px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            erledigt_am: datum,
            wirksamkeit_bemerkung: bemerkung,
          });
        }}
      >
        <h2 className="mb-2 text-lg font-semibold">Finding als erledigt markieren</h2>
        <p className="text-sm text-muted-foreground">
          Dokumentiert die Wirksamkeit der Maßnahme. Der Eintrag wird in der
          Audit-Akte gespeichert.
        </p>
        <div className="mt-3 space-y-3">
          <div>
            <Label>Erledigt am</Label>
            <Input
              type="date"
              value={datum}
              onChange={(e) => setDatum(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Wirksamkeits-Bemerkung</Label>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm"
              rows={4}
              value={bemerkung}
              onChange={(e) => setBemerkung(e.target.value)}
              placeholder="Wie wurde die Wirksamkeit geprüft?"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Speichern
          </Button>
        </div>
      </form>
    </div>
  );
}
