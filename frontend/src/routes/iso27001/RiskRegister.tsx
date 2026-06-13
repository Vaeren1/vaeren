/**
 * Risiko-Register mit Tabelle, Create-/Edit-Modal, LLM-Treatment-Vorschlag
 * und GF-only-Akzeptanz-Workflow. Optional 5x5-Heatmap-View.
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
  type IsmsAsset,
  type IsmsRiskAssessment,
  type LlmEntwurfResponse,
  akzeptiereRisiko,
  createRisiko,
  listAssets,
  listRisiken,
  llmTreatmentVorschlag,
  updateRisiko,
} from "@/lib/api/iso27001";
import { useMitarbeiterList } from "@/lib/api/mitarbeiter";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { toast } from "sonner";

type Treatment = IsmsRiskAssessment["treatment"];

const TREATMENT_VALUES: Treatment[] = [
  "reduzieren",
  "akzeptieren",
  "uebertragen",
  "vermeiden",
];

const TREATMENT_LABELS: Record<Treatment, string> = {
  reduzieren: "Reduzieren",
  akzeptieren: "Akzeptieren",
  uebertragen: "Übertragen",
  vermeiden: "Vermeiden",
};

function scoreBadgeClass(score: number): string {
  if (score >= 16) return "bg-rose-100 text-rose-800 border-rose-300";
  if (score >= 7) return "bg-amber-100 text-amber-800 border-amber-300";
  return "bg-emerald-100 text-emerald-800 border-emerald-300";
}

export function Iso27001RiskRegister() {
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const isGf = user?.tenant_role === "geschaeftsfuehrer";

  const { data, isLoading, isError } = useQuery({
    queryKey: ["iso27001-risiken"],
    queryFn: listRisiken,
  });
  const { data: assets } = useQuery({
    queryKey: ["iso27001-assets"],
    queryFn: listAssets,
  });

  const [view, setView] = useState<"liste" | "heatmap">("liste");
  const [showCreate, setShowCreate] = useState(false);
  const [editRisiko, setEditRisiko] = useState<IsmsRiskAssessment | null>(null);
  const [akzeptierenRisiko, setAkzeptierenRisiko] =
    useState<IsmsRiskAssessment | null>(null);

  const createMut = useMutation({
    mutationFn: createRisiko,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-risiken"] });
      qc.invalidateQueries({ queryKey: ["iso27001-dashboard"] });
      toast.success("Risiko angelegt.");
      setShowCreate(false);
    },
    onError: (e: unknown) => {
      toast.error(e instanceof Error ? e.message : "Fehler beim Anlegen");
    },
  });

  const updateMut = useMutation({
    mutationFn: (vars: { id: number; payload: Partial<IsmsRiskAssessment> }) =>
      updateRisiko(vars.id, vars.payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-risiken"] });
      qc.invalidateQueries({ queryKey: ["iso27001-dashboard"] });
      toast.success("Risiko aktualisiert.");
      setEditRisiko(null);
    },
    onError: (e: unknown) => {
      toast.error(e instanceof Error ? e.message : "Fehler beim Aktualisieren");
    },
  });

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>ISMS-Risiko-Register</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Risk-Score = Likelihood × Impact (1–25). Vom Tenant verantwortet.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="rounded border bg-muted/40 p-0.5 text-xs">
              <button
                type="button"
                className={`rounded px-2 py-1 ${view === "liste" ? "bg-white shadow-sm" : ""}`}
                onClick={() => setView("liste")}
              >
                Liste
              </button>
              <button
                type="button"
                className={`rounded px-2 py-1 ${view === "heatmap" ? "bg-white shadow-sm" : ""}`}
                onClick={() => setView("heatmap")}
              >
                Heatmap
              </button>
            </div>
            <Button onClick={() => setShowCreate(true)}>
              + Risiko anlegen
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isError ? (
          <p className="text-destructive">
            Risiken konnten nicht geladen werden — bitte Seite neu laden.
          </p>
        ) : isLoading ? (
          <p>Lade …</p>
        ) : !data || data.results.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            Noch keine Risiken erfasst. Klick „+ Risiko anlegen", um zu
            beginnen.
          </p>
        ) : view === "liste" ? (
          <RisikoListe
            risiken={data.results}
            assets={assets?.results ?? []}
            onEdit={setEditRisiko}
            onAkzeptieren={setAkzeptierenRisiko}
            isGf={isGf}
          />
        ) : (
          <RisikoHeatmap risiken={data.results} />
        )}
      </CardContent>

      {showCreate && (
        <RisikoForm
          mode="create"
          assets={assets?.results ?? []}
          onCancel={() => setShowCreate(false)}
          onSubmit={(payload) => createMut.mutate(payload)}
          isPending={createMut.isPending}
        />
      )}

      {editRisiko && (
        <RisikoForm
          mode="edit"
          assets={assets?.results ?? []}
          initial={editRisiko}
          onCancel={() => setEditRisiko(null)}
          onSubmit={(payload) =>
            updateMut.mutate({ id: editRisiko.id, payload })
          }
          isPending={updateMut.isPending}
        />
      )}

      {akzeptierenRisiko && (
        <AkzeptanzDialog
          risiko={akzeptierenRisiko}
          onCancel={() => setAkzeptierenRisiko(null)}
          onSuccess={() => setAkzeptierenRisiko(null)}
        />
      )}
    </Card>
  );
}

// ---------------------------------------------------------------------------
// Liste
// ---------------------------------------------------------------------------

function RisikoListe({
  risiken,
  assets,
  onEdit,
  onAkzeptieren,
  isGf,
}: {
  risiken: IsmsRiskAssessment[];
  assets: IsmsAsset[];
  onEdit: (r: IsmsRiskAssessment) => void;
  onAkzeptieren: (r: IsmsRiskAssessment) => void;
  isGf: boolean;
}) {
  const assetMap = useMemo(() => {
    const m = new Map<number, string>();
    for (const a of assets) m.set(a.id, a.name);
    return m;
  }, [assets]);

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Titel</TableHead>
          <TableHead>Asset</TableHead>
          <TableHead>L</TableHead>
          <TableHead>I</TableHead>
          <TableHead>Score</TableHead>
          <TableHead>Treatment</TableHead>
          <TableHead>Akzeptiert</TableHead>
          <TableHead>Aktionen</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {risiken.map((r) => {
          const score = r.risk_score_brutto;
          const canAkzeptieren =
            r.restrisiko_likelihood != null &&
            r.restrisiko_impact != null &&
            r.akzeptiert_von == null;
          return (
            <TableRow key={r.id}>
              <TableCell className="font-medium">{r.titel}</TableCell>
              <TableCell>{assetMap.get(r.asset) ?? `#${r.asset}`}</TableCell>
              <TableCell>{r.likelihood}</TableCell>
              <TableCell>{r.impact}</TableCell>
              <TableCell>
                <span
                  className={`inline-flex rounded border px-2 py-0.5 text-xs font-mono ${scoreBadgeClass(score)}`}
                >
                  {score}
                </span>
              </TableCell>
              <TableCell>{TREATMENT_LABELS[r.treatment]}</TableCell>
              <TableCell className="text-xs">
                {r.akzeptiert_am ? (
                  <span className="text-emerald-700">
                    ✓ {r.akzeptiert_am.slice(0, 10)}
                  </span>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </TableCell>
              <TableCell className="space-x-1">
                <Button size="sm" variant="outline" onClick={() => onEdit(r)}>
                  Bearbeiten
                </Button>
                {canAkzeptieren && isGf && (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => onAkzeptieren(r)}
                  >
                    Akzeptieren
                  </Button>
                )}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

// ---------------------------------------------------------------------------
// Heatmap (pragmatisch, 5x5-HTML-Grid)
// ---------------------------------------------------------------------------

function RisikoHeatmap({ risiken }: { risiken: IsmsRiskAssessment[] }) {
  // Achsen: Likelihood horizontal (1..5), Impact vertikal (5..1 oben→unten)
  const cells: Record<string, IsmsRiskAssessment[]> = {};
  for (const r of risiken) {
    const key = `${r.likelihood}-${r.impact}`;
    if (!cells[key]) cells[key] = [];
    cells[key].push(r);
  }

  function cellBg(score: number, hasRisks: boolean): string {
    if (!hasRisks) return "bg-muted/20";
    if (score >= 16) return "bg-rose-200";
    if (score >= 7) return "bg-amber-200";
    return "bg-emerald-200";
  }

  return (
    <div className="space-y-2">
      <div className="text-xs text-muted-foreground">
        Achsen: Likelihood (X, 1–5) × Impact (Y, 5 oben). Zellen-Score = L × I.
      </div>
      <div className="grid grid-cols-[auto_repeat(5,minmax(64px,1fr))] gap-1 text-xs">
        <div />
        {[1, 2, 3, 4, 5].map((l) => (
          <div key={`hx-${l}`} className="text-center font-medium">
            L={l}
          </div>
        ))}
        {[5, 4, 3, 2, 1].map((i) => (
          <RiskmapRow
            key={`row-${i}`}
            impact={i}
            cells={cells}
            cellBg={cellBg}
          />
        ))}
      </div>
    </div>
  );
}

function RiskmapRow({
  impact,
  cells,
  cellBg,
}: {
  impact: number;
  cells: Record<string, IsmsRiskAssessment[]>;
  cellBg: (score: number, hasRisks: boolean) => string;
}) {
  return (
    <>
      <div className="text-right pr-2 font-medium">I={impact}</div>
      {[1, 2, 3, 4, 5].map((l) => {
        const list = cells[`${l}-${impact}`] ?? [];
        const score = l * impact;
        return (
          <div
            key={`cell-${l}-${impact}`}
            className={`relative aspect-square rounded border ${cellBg(score, list.length > 0)} p-1`}
            title={list.map((r) => r.titel).join("\n") || `Score ${score}`}
          >
            <div className="absolute top-0.5 left-1 text-[10px] text-muted-foreground">
              {score}
            </div>
            {list.length > 0 && (
              <div className="flex h-full items-center justify-center text-base font-semibold">
                {list.length}
              </div>
            )}
          </div>
        );
      })}
    </>
  );
}

// ---------------------------------------------------------------------------
// Create/Edit-Form
// ---------------------------------------------------------------------------

function RisikoForm({
  mode,
  assets,
  initial,
  onCancel,
  onSubmit,
  isPending,
}: {
  mode: "create" | "edit";
  assets: IsmsAsset[];
  initial?: IsmsRiskAssessment;
  onCancel: () => void;
  onSubmit: (payload: Partial<IsmsRiskAssessment>) => void;
  isPending: boolean;
}) {
  const [titel, setTitel] = useState(initial?.titel ?? "");
  const [threat, setThreat] = useState(initial?.threat ?? "");
  const [vulnerability, setVulnerability] = useState(
    initial?.vulnerability ?? "",
  );
  const [likelihood, setLikelihood] = useState(initial?.likelihood ?? 3);
  const [impact, setImpact] = useState(initial?.impact ?? 3);
  const [assetId, setAssetId] = useState<number | "">(initial?.asset ?? "");
  const [treatment, setTreatment] = useState<Treatment>(
    initial?.treatment ?? "reduzieren",
  );
  const [treatmentPlan, setTreatmentPlan] = useState(
    initial?.treatment_plan ?? "",
  );
  const [restL, setRestL] = useState<number | "">(
    initial?.restrisiko_likelihood ?? "",
  );
  const [restI, setRestI] = useState<number | "">(
    initial?.restrisiko_impact ?? "",
  );
  const [vorschlag, setVorschlag] = useState<LlmEntwurfResponse | null>(null);
  const [loadingVorschlag, setLoadingVorschlag] = useState(false);

  async function generiereVorschlag() {
    if (!initial) {
      toast.error("Vorschlag erst nach Speichern verfügbar.");
      return;
    }
    setLoadingVorschlag(true);
    try {
      const result = await llmTreatmentVorschlag(initial.id);
      setVorschlag(result);
    } catch (e) {
      toast.error(e instanceof Error ? e.message : "Vorschlag fehlgeschlagen");
    } finally {
      setLoadingVorschlag(false);
    }
  }

  function uebernehmen() {
    if (vorschlag) {
      setTreatmentPlan(
        treatmentPlan
          ? `${treatmentPlan}\n\n--- LLM-Vorschlag ---\n${vorschlag.entwurf}`
          : vorschlag.entwurf,
      );
      toast.success("Vorschlag in Plan kopiert.");
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 overflow-y-auto py-8">
      <form
        className="w-[720px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          if (assetId === "") {
            toast.error("Asset auswählen.");
            return;
          }
          onSubmit({
            titel,
            threat,
            vulnerability,
            likelihood,
            impact,
            asset: Number(assetId),
            treatment,
            treatment_plan: treatmentPlan,
            restrisiko_likelihood: restL === "" ? null : Number(restL),
            restrisiko_impact: restI === "" ? null : Number(restI),
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">
          {mode === "create" ? "Neues Risiko" : "Risiko bearbeiten"}
        </h2>
        <div className="space-y-3">
          <div>
            <Label>Titel</Label>
            <Input
              value={titel}
              onChange={(e) => setTitel(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Threat (Bedrohung)</Label>
              <textarea
                className="w-full rounded border px-3 py-2 text-sm"
                rows={2}
                value={threat}
                onChange={(e) => setThreat(e.target.value)}
              />
            </div>
            <div>
              <Label>Vulnerability (Schwachstelle)</Label>
              <textarea
                className="w-full rounded border px-3 py-2 text-sm"
                rows={2}
                value={vulnerability}
                onChange={(e) => setVulnerability(e.target.value)}
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <Label>Likelihood (1–5)</Label>
              <select
                className="w-full rounded border px-3 py-2 text-sm"
                value={likelihood}
                onChange={(e) => setLikelihood(Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Impact (1–5)</Label>
              <select
                className="w-full rounded border px-3 py-2 text-sm"
                value={impact}
                onChange={(e) => setImpact(Number(e.target.value))}
              >
                {[1, 2, 3, 4, 5].map((n) => (
                  <option key={n} value={n}>
                    {n}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Score (brutto)</Label>
              <div className="rounded border px-3 py-2 text-sm font-mono bg-muted/30">
                {likelihood * impact}
              </div>
            </div>
          </div>
          <div>
            <Label>Asset</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={assetId}
              onChange={(e) =>
                setAssetId(e.target.value ? Number(e.target.value) : "")
              }
              required
            >
              <option value="">— Asset wählen —</option>
              {assets.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Treatment</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={treatment}
              onChange={(e) => setTreatment(e.target.value as Treatment)}
            >
              {TREATMENT_VALUES.map((t) => (
                <option key={t} value={t}>
                  {TREATMENT_LABELS[t]}
                </option>
              ))}
            </select>
          </div>
          <div>
            <div className="flex items-center justify-between">
              <Label>Treatment-Plan</Label>
              {mode === "edit" && (
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={generiereVorschlag}
                  disabled={loadingVorschlag}
                >
                  {loadingVorschlag ? "Lade …" : "Vorschlag generieren"}
                </Button>
              )}
            </div>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm"
              rows={4}
              value={treatmentPlan}
              onChange={(e) => setTreatmentPlan(e.target.value)}
              placeholder="Wie wird das Risiko behandelt?"
            />
            {vorschlag && (
              <div className="mt-2 rounded border-2 border-amber-300 bg-amber-50 p-3 text-sm">
                <div className="mb-1 text-xs font-semibold text-amber-900">
                  LLM-Vorschlag — bitte rechtlich/fachlich prüfen
                </div>
                <p className="mb-2 text-xs italic text-amber-900">
                  {vorschlag.rdg_disclaimer}
                </p>
                <pre className="whitespace-pre-wrap text-xs">
                  {vorschlag.entwurf}
                </pre>
                <div className="mt-2 flex justify-end gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => setVorschlag(null)}
                  >
                    Verwerfen
                  </Button>
                  <Button type="button" size="sm" onClick={uebernehmen}>
                    Übernehmen
                  </Button>
                </div>
              </div>
            )}
          </div>
          {mode === "edit" && (
            <div className="grid grid-cols-2 gap-3 rounded bg-muted/30 p-3">
              <div>
                <Label>Restrisiko Likelihood</Label>
                <select
                  className="w-full rounded border px-3 py-2 text-sm"
                  value={restL}
                  onChange={(e) =>
                    setRestL(e.target.value ? Number(e.target.value) : "")
                  }
                >
                  <option value="">— nicht bewertet —</option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Restrisiko Impact</Label>
                <select
                  className="w-full rounded border px-3 py-2 text-sm"
                  value={restI}
                  onChange={(e) =>
                    setRestI(e.target.value ? Number(e.target.value) : "")
                  }
                >
                  <option value="">— nicht bewertet —</option>
                  {[1, 2, 3, 4, 5].map((n) => (
                    <option key={n} value={n}>
                      {n}
                    </option>
                  ))}
                </select>
              </div>
              <p className="col-span-2 text-xs text-muted-foreground">
                Restrisiko ist Voraussetzung für GF-Akzeptanz.
              </p>
            </div>
          )}
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            {mode === "create" ? "Anlegen" : "Speichern"}
          </Button>
        </div>
      </form>
    </div>
  );
}

// ---------------------------------------------------------------------------
// GF-Akzeptanz-Dialog
// ---------------------------------------------------------------------------

function AkzeptanzDialog({
  risiko,
  onCancel,
  onSuccess,
}: {
  risiko: IsmsRiskAssessment;
  onCancel: () => void;
  onSuccess: () => void;
}) {
  const qc = useQueryClient();
  const { data: mitarbeiter } = useMitarbeiterList();
  const [mitarbeiterId, setMitarbeiterId] = useState<number | "">("");

  const mut = useMutation({
    mutationFn: () =>
      akzeptiereRisiko(
        risiko.id,
        mitarbeiterId === "" ? 0 : Number(mitarbeiterId),
      ),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-risiken"] });
      qc.invalidateQueries({ queryKey: ["iso27001-dashboard"] });
      toast.success("Risiko von GF akzeptiert.");
      onSuccess();
    },
    onError: (e: unknown) => {
      const msg =
        e && typeof e === "object" && "body" in e
          ? (() => {
              const body = (e as { body: unknown }).body;
              if (
                body &&
                typeof body === "object" &&
                "detail" in body &&
                typeof (body as { detail: unknown }).detail === "string"
              ) {
                return (body as { detail: string }).detail;
              }
              return "Akzeptanz fehlgeschlagen";
            })()
          : e instanceof Error
            ? e.message
            : "Akzeptanz fehlgeschlagen";
      toast.error(msg);
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[560px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          if (!mitarbeiterId) {
            toast.error("Akzeptierender Mitarbeiter erforderlich.");
            return;
          }
          mut.mutate();
        }}
      >
        <h2 className="mb-2 text-lg font-semibold">Restrisiko akzeptieren</h2>
        <p className="text-sm text-muted-foreground">
          Mit Akzeptanz bestätigt die Geschäftsführung formal das verbleibende
          Risiko bei <strong>{risiko.titel}</strong> (Restrisiko-Score{" "}
          {risiko.risk_score_netto ?? "—"}).
        </p>
        <div className="mt-3">
          <Label>Akzeptiert durch (Mitarbeiter)</Label>
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={mitarbeiterId}
            onChange={(e) =>
              setMitarbeiterId(e.target.value ? Number(e.target.value) : "")
            }
            required
          >
            <option value="">— Mitarbeiter wählen —</option>
            {(mitarbeiter?.results ?? []).map((m) => (
              <option key={m.id} value={m.id}>
                {m.vorname} {m.nachname} ({m.rolle})
              </option>
            ))}
          </select>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={mut.isPending}>
            Akzeptieren
          </Button>
        </div>
      </form>
    </div>
  );
}
