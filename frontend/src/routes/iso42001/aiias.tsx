/**
 * AIIAs — Liste + einfacher Wizard (5 Felder, kein Multi-Step im MVP).
 *
 * Phase-3 MVP: Form-basiert. Wizard-Multistep ist Phase-3b-Polish.
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
  type AIIAStatus,
  AIIA_STATUS_LABELS,
  type AiImpactAssessment,
  createAIIA,
  freigebenAIIA,
  listAIIAs,
  listAiSystems,
  setAIIAStatus,
  updateAIIA,
  vorschlagAuswirkungsKategorien,
  vorschlagRisiken,
} from "@/lib/api/iso42001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

const AUSWIRKUNGS_KATEGORIEN = [
  "grundrechte",
  "gesundheit",
  "umwelt",
  "sozial",
  "oekonomisch",
  "informationell",
];

export function Iso42001AIIAsPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["iso42001-aiias"],
    queryFn: listAIIAs,
  });
  const { data: systems } = useQuery({
    queryKey: ["iso42001-ai-systems"],
    queryFn: listAiSystems,
  });
  const [showForm, setShowForm] = useState(false);
  const [edit, setEdit] = useState<AiImpactAssessment | null>(null);

  const createMut = useMutation({
    mutationFn: createAIIA,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-aiias"] });
      toast.success("AIIA-Entwurf angelegt.");
      setShowForm(false);
    },
  });

  const statusMut = useMutation({
    mutationFn: (vars: { id: number; status: AIIAStatus }) =>
      setAIIAStatus(vars.id, vars.status),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-aiias"] });
      toast.success("Status gewechselt.");
    },
    onError: (e: unknown) => {
      toast.error(
        e instanceof Error ? e.message : "Status-Wechsel fehlgeschlagen",
      );
    },
  });

  const freigabeMut = useMutation({
    mutationFn: freigebenAIIA,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-aiias"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("AIIA freigegeben (4-Augen-Prinzip).");
    },
    onError: (e: unknown) => {
      toast.error(e instanceof Error ? e.message : "Freigabe fehlgeschlagen");
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">AI Impact Assessments</h1>
          <p className="text-sm text-muted-foreground">
            ISO/IEC 42001 Annex A.5 — strukturierte Bewertung der Auswirkungen
            eines KI-Systems. 4-Augen-Approval enforced (Ersteller ≠ Approver).
          </p>
        </div>
        <Button
          onClick={() => setShowForm(true)}
          disabled={!systems?.results.length}
        >
          + Neue AIIA
        </Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          {isLoading && <p>Lade …</p>}
          {isError && (
            <p className="text-destructive">
              AIIAs konnten nicht geladen werden — bitte Seite neu laden.
            </p>
          )}
          {data && data.results.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Keine AIIAs erfasst.
            </p>
          )}
          {data && data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Titel</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Approval</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.results.map((a) => (
                  <TableRow key={a.id}>
                    <TableCell className="font-medium">{a.titel}</TableCell>
                    <TableCell>v{a.version}</TableCell>
                    <TableCell>{AIIA_STATUS_LABELS[a.status]}</TableCell>
                    <TableCell>{a.approved_at ? "Ja" : "—"}</TableCell>
                    <TableCell className="space-x-1 text-right">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => setEdit(a)}
                      >
                        Bearbeiten
                      </Button>
                      {a.status === "entwurf" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            statusMut.mutate({ id: a.id, status: "bewertung" })
                          }
                        >
                          In Bewertung
                        </Button>
                      )}
                      {a.status === "bewertung" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() =>
                            statusMut.mutate({
                              id: a.id,
                              status: "approval_offen",
                            })
                          }
                        >
                          Approval anfordern
                        </Button>
                      )}
                      {a.status === "approval_offen" && (
                        <Button
                          size="sm"
                          onClick={() => freigabeMut.mutate(a.id)}
                        >
                          Freigeben (GF)
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

      {showForm && systems && (
        <AIIAForm
          systems={systems.results}
          onCancel={() => setShowForm(false)}
          onSubmit={createMut.mutate}
          isPending={createMut.isPending}
        />
      )}

      {edit && (
        <AIIAEditDrawer
          aiia={edit}
          onClose={() => setEdit(null)}
          onSaved={() => qc.invalidateQueries({ queryKey: ["iso42001-aiias"] })}
        />
      )}
    </div>
  );
}

function AIIAForm({
  systems,
  onCancel,
  onSubmit,
  isPending,
}: {
  systems: { id: number; ki_tool_name: string }[];
  onCancel: () => void;
  onSubmit: (payload: {
    ai_system: number;
    titel: string;
    zweck_beschreibung: string;
    betroffene_personen: string;
  }) => void;
  isPending: boolean;
}) {
  const [systemId, setSystemId] = useState<number>(systems[0]?.id ?? 0);
  const [titel, setTitel] = useState("");
  const [zweck, setZweck] = useState("");
  const [betroffene, setBetroffene] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[640px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            ai_system: systemId,
            titel,
            zweck_beschreibung: zweck,
            betroffene_personen: betroffene,
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">Neue AIIA anlegen</h2>
        <div className="space-y-3">
          <div>
            <Label>AI-System</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={systemId}
              onChange={(e) => setSystemId(Number(e.target.value))}
              required
            >
              {systems.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.ki_tool_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Titel</Label>
            <Input
              value={titel}
              onChange={(e) => setTitel(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Zweck-Beschreibung</Label>
            <textarea
              rows={3}
              className="w-full rounded border px-3 py-2 text-sm"
              value={zweck}
              onChange={(e) => setZweck(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Betroffene Personen</Label>
            <textarea
              rows={2}
              className="w-full rounded border px-3 py-2 text-sm"
              placeholder="Mitarbeiter, Kunden, Bewerber, Bürger ..."
              value={betroffene}
              onChange={(e) => setBetroffene(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Entwurf anlegen
          </Button>
        </div>
      </form>
    </div>
  );
}

function AIIAEditDrawer({
  aiia,
  onClose,
  onSaved,
}: {
  aiia: AiImpactAssessment;
  onClose: () => void;
  onSaved: () => void;
}) {
  const readOnly =
    aiia.status === "freigegeben" || aiia.status === "archiviert";
  const [kats, setKats] = useState<string[]>(aiia.auswirkungs_kategorien);
  const [mitigationen, setMitigationen] = useState(aiia.mitigationen);
  const [restrisiko, setRestrisiko] = useState(aiia.restrisiko);
  const [restrisikoOk, setRestrisikoOk] = useState(aiia.restrisiko_akzeptabel);
  const [risiken, setRisiken] = useState<Array<Record<string, string>>>(
    aiia.risiken_identifiziert,
  );

  const saveMut = useMutation({
    mutationFn: () =>
      updateAIIA(aiia.id, {
        auswirkungs_kategorien: kats,
        risiken_identifiziert: risiken,
        mitigationen,
        restrisiko,
        restrisiko_akzeptabel: restrisikoOk,
      }),
    onSuccess: () => {
      toast.success("AIIA gespeichert.");
      onSaved();
      onClose();
    },
  });

  const vorschlagKatMut = useMutation({
    mutationFn: () =>
      vorschlagAuswirkungsKategorien({
        kategorie: "sonstiges",
        datenkategorie_sensibilitaet: "gewoehnlich",
        zweck: aiia.zweck_beschreibung,
      }),
    onSuccess: (v) => {
      setKats(Array.from(new Set([...kats, ...v.kategorien])));
      toast.info(
        `KI-Vorschlag (${v.kategorien.length} Kategorien) — bitte prüfen.`,
      );
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "LLM-Fehler"),
  });

  const vorschlagRisikenMut = useMutation({
    mutationFn: () =>
      vorschlagRisiken({
        kategorie: "sonstiges",
        zweck: aiia.zweck_beschreibung,
        betroffene: aiia.betroffene_personen,
      }),
    onSuccess: (v) => {
      setRisiken([...risiken, ...v.risiken]);
      toast.info(`KI-Vorschlag (${v.risiken.length} Risiken) — bitte prüfen.`);
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "LLM-Fehler"),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="max-h-[90vh] w-[760px] max-w-full overflow-y-auto rounded-md bg-white p-6 shadow-xl">
        <h2 className="mb-1 text-lg font-semibold">
          AIIA v{aiia.version}: {aiia.titel}
        </h2>
        <p className="mb-3 text-xs text-muted-foreground">
          Status: {AIIA_STATUS_LABELS[aiia.status]}
          {readOnly && " (read-only)"}
        </p>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Auswirkungs-Kategorien</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="mb-2 flex flex-wrap gap-2">
                {AUSWIRKUNGS_KATEGORIEN.map((k) => (
                  <label key={k} className="flex items-center gap-1 text-sm">
                    <input
                      type="checkbox"
                      disabled={readOnly}
                      checked={kats.includes(k)}
                      onChange={(e) =>
                        setKats(
                          e.target.checked
                            ? [...kats, k]
                            : kats.filter((x) => x !== k),
                        )
                      }
                    />
                    {k}
                  </label>
                ))}
              </div>
              {!readOnly && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => vorschlagKatMut.mutate()}
                  disabled={vorschlagKatMut.isPending}
                >
                  KI-Vorschlag holen
                </Button>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Risiken</CardTitle>
            </CardHeader>
            <CardContent>
              {risiken.map((r, i) => (
                <div
                  key={`risiko-${i}-${r.risiko ?? ""}`}
                  className="rounded border bg-amber-50 px-2 py-1 text-xs mb-1"
                >
                  <strong>{r.risiko}</strong> — wahrscheinlichkeit:{" "}
                  {r.wahrscheinlichkeit}, schwere: {r.schweregrad}
                </div>
              ))}
              {!readOnly && (
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => vorschlagRisikenMut.mutate()}
                  disabled={vorschlagRisikenMut.isPending}
                >
                  KI-Vorschlag holen
                </Button>
              )}
            </CardContent>
          </Card>

          <div>
            <Label>Mitigationen</Label>
            <textarea
              rows={3}
              className="w-full rounded border px-3 py-2 text-sm"
              value={mitigationen}
              onChange={(e) => setMitigationen(e.target.value)}
              disabled={readOnly}
            />
          </div>
          <div>
            <Label>Restrisiko-Beschreibung</Label>
            <textarea
              rows={2}
              className="w-full rounded border px-3 py-2 text-sm"
              value={restrisiko}
              onChange={(e) => setRestrisiko(e.target.value)}
              disabled={readOnly}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={restrisikoOk}
              disabled={readOnly}
              onChange={(e) => setRestrisikoOk(e.target.checked)}
            />
            Restrisiko ist akzeptabel
          </label>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="outline" onClick={onClose}>
            Schließen
          </Button>
          {!readOnly && (
            <Button
              onClick={() => saveMut.mutate()}
              disabled={saveMut.isPending}
            >
              Speichern
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
