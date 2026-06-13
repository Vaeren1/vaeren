/**
 * KI-Vorfälle (AiIncident) — Liste + Form + Eskalations-Dialog.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
  type AiIncident,
  type AiIncidentSchweregrad,
  type AiIncidentTyp,
  INCIDENT_TYP_LABELS,
  createIncident,
  eskalierenAlsDatenpanne,
  incidentAbschliessen,
  listAiSystems,
  listIncidents,
} from "@/lib/api/iso42001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

const TYP_VALUES: AiIncidentTyp[] = [
  "bias_entdeckt",
  "output_fehler",
  "datenleck",
  "drift",
  "missbrauch",
  "sonstiges",
];

const SCHWERE_VALUES: AiIncidentSchweregrad[] = [
  "niedrig",
  "mittel",
  "hoch",
  "kritisch",
];

export function Iso42001IncidentsPage() {
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["iso42001-incidents"],
    queryFn: listIncidents,
  });
  const { data: systems } = useQuery({
    queryKey: ["iso42001-ai-systems"],
    queryFn: listAiSystems,
  });
  const [showForm, setShowForm] = useState(false);
  const [eskalate, setEskalate] = useState<AiIncident | null>(null);
  const [abschliessen, setAbschliessen] = useState<AiIncident | null>(null);

  const createMut = useMutation({
    mutationFn: createIncident,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-incidents"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("Vorfall erfasst.");
      setShowForm(false);
    },
  });

  const eskalateMut = useMutation({
    mutationFn: (vars: { id: number; force: boolean }) =>
      eskalierenAlsDatenpanne(vars.id, vars.force),
    onSuccess: (resp) => {
      qc.invalidateQueries({ queryKey: ["iso42001-incidents"] });
      qc.invalidateQueries({ queryKey: ["datenpannen"] });
      toast.success(`Als Datenpanne #${resp.datenpanne_id} eskaliert.`);
      setEskalate(null);
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Fehler bei Eskalation";
      toast.error(msg);
    },
  });

  const abschliessenMut = useMutation({
    mutationFn: (vars: {
      id: number;
      abgeschlossen_am: string;
      korrekturmassnahme: string;
    }) =>
      incidentAbschliessen(vars.id, {
        abgeschlossen_am: vars.abgeschlossen_am,
        korrekturmassnahme: vars.korrekturmassnahme,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-incidents"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("Vorfall abgeschlossen.");
      setAbschliessen(null);
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Fehler beim Abschluss";
      toast.error(msg);
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">KI-Vorfälle</h1>
          <p className="text-sm text-muted-foreground">
            Bias, fehlerhafte Outputs, Drift, Missbrauch — passiv dokumentiert,
            bei PII-Bezug nach DSGVO Art. 33 als Datenpanne eskalierbar.
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}>+ Vorfall melden</Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          {isLoading && <p>Lade …</p>}
          {isError && (
            <p className="text-destructive">
              Vorfälle konnten nicht geladen werden — bitte Seite neu laden.
            </p>
          )}
          {data && data.results.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Keine Vorfälle erfasst.
            </p>
          )}
          {data && data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Titel</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Schweregrad</TableHead>
                  <TableHead>Entdeckt</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Datenpanne</TableHead>
                  <TableHead>Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.results.map((i) => (
                  <TableRow key={i.id}>
                    <TableCell className="font-medium">{i.titel}</TableCell>
                    <TableCell>{INCIDENT_TYP_LABELS[i.typ]}</TableCell>
                    <TableCell>{i.schweregrad}</TableCell>
                    <TableCell>{i.entdeckt_am}</TableCell>
                    <TableCell>
                      {i.offen ? (
                        <span className="text-rose-700">
                          offen seit {i.offen_seit_tagen}d
                        </span>
                      ) : (
                        <span className="text-emerald-700">abgeschlossen</span>
                      )}
                    </TableCell>
                    <TableCell>
                      {i.datenpanne ? (
                        <Link
                          to={`/datenpannen/${i.datenpanne}`}
                          className="underline text-amber-700"
                        >
                          #{i.datenpanne}
                        </Link>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setEskalate(i)}
                        >
                          Als Datenpanne eskalieren
                        </Button>
                      )}
                    </TableCell>
                    <TableCell>
                      {i.offen && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => setAbschliessen(i)}
                        >
                          Abschließen
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

      {showForm && (
        <IncidentForm
          systems={systems?.results ?? []}
          onCancel={() => setShowForm(false)}
          onSubmit={(payload) => createMut.mutate(payload)}
          isPending={createMut.isPending}
        />
      )}

      {eskalate && (
        <EskalationsDialog
          incident={eskalate}
          onCancel={() => setEskalate(null)}
          onConfirm={(force) => eskalateMut.mutate({ id: eskalate.id, force })}
          isPending={eskalateMut.isPending}
        />
      )}

      {abschliessen && (
        <AbschluessenDialog
          incident={abschliessen}
          onCancel={() => setAbschliessen(null)}
          onConfirm={(datum, korrektur) =>
            abschliessenMut.mutate({
              id: abschliessen.id,
              abgeschlossen_am: datum,
              korrekturmassnahme: korrektur,
            })
          }
          isPending={abschliessenMut.isPending}
        />
      )}
    </div>
  );
}

function AbschluessenDialog({
  incident,
  onCancel,
  onConfirm,
  isPending,
}: {
  incident: AiIncident;
  onCancel: () => void;
  onConfirm: (datum: string, korrektur: string) => void;
  isPending: boolean;
}) {
  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 10));
  const [korrektur, setKorrektur] = useState(incident.korrekturmassnahme ?? "");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[560px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onConfirm(datum, korrektur);
        }}
      >
        <h2 className="mb-2 text-lg font-semibold">Vorfall abschließen</h2>
        <p className="text-sm text-muted-foreground">
          Bestätigt, dass der Vorfall <strong>{incident.titel}</strong>{" "}
          bearbeitet ist. Die Korrekturmaßnahme wird in der Akte dokumentiert.
        </p>
        <div className="mt-3 space-y-3">
          <div>
            <Label>Abgeschlossen am</Label>
            <Input
              type="date"
              value={datum}
              onChange={(e) => setDatum(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Korrekturmaßnahme</Label>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm"
              rows={4}
              value={korrektur}
              onChange={(e) => setKorrektur(e.target.value)}
              placeholder="Was wurde dauerhaft geändert, damit der Vorfall sich nicht wiederholt?"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Abschließen
          </Button>
        </div>
      </form>
    </div>
  );
}

function IncidentForm({
  systems,
  onCancel,
  onSubmit,
  isPending,
}: {
  systems: { id: number; ki_tool_name: string }[];
  onCancel: () => void;
  onSubmit: (payload: {
    titel: string;
    typ: AiIncidentTyp;
    schweregrad: AiIncidentSchweregrad;
    entdeckt_am: string;
    beschreibung: string;
    ai_system?: number | null;
  }) => void;
  isPending: boolean;
}) {
  const [titel, setTitel] = useState("");
  const [typ, setTyp] = useState<AiIncidentTyp>("output_fehler");
  const [schwere, setSchwere] = useState<AiIncidentSchweregrad>("mittel");
  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 10));
  const [beschreibung, setBeschreibung] = useState("");
  const [systemId, setSystemId] = useState<number | "">("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[640px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            titel,
            typ,
            schweregrad: schwere,
            entdeckt_am: datum,
            beschreibung,
            ai_system: systemId === "" ? null : Number(systemId),
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">Neuer KI-Vorfall</h2>
        <div className="space-y-3">
          <div>
            <Label>Titel</Label>
            <Input
              value={titel}
              onChange={(e) => setTitel(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-3 gap-2">
            <div>
              <Label>Typ</Label>
              <select
                className="w-full rounded border px-3 py-2 text-sm"
                value={typ}
                onChange={(e) => setTyp(e.target.value as AiIncidentTyp)}
              >
                {TYP_VALUES.map((t) => (
                  <option key={t} value={t}>
                    {INCIDENT_TYP_LABELS[t]}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Schweregrad</Label>
              <select
                className="w-full rounded border px-3 py-2 text-sm"
                value={schwere}
                onChange={(e) =>
                  setSchwere(e.target.value as AiIncidentSchweregrad)
                }
              >
                {SCHWERE_VALUES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <Label>Entdeckt am</Label>
              <Input
                type="date"
                value={datum}
                onChange={(e) => setDatum(e.target.value)}
                required
              />
            </div>
          </div>
          <div>
            <Label>Betroffenes AI-System (optional)</Label>
            <select
              className="w-full rounded border px-3 py-2 text-sm"
              value={systemId}
              onChange={(e) =>
                setSystemId(e.target.value ? Number(e.target.value) : "")
              }
            >
              <option value="">— kein bestimmtes System —</option>
              {systems.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.ki_tool_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <Label>Beschreibung</Label>
            <textarea
              className="w-full rounded border px-3 py-2 text-sm"
              rows={4}
              value={beschreibung}
              onChange={(e) => setBeschreibung(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Vorfall erfassen
          </Button>
        </div>
      </form>
    </div>
  );
}

function EskalationsDialog({
  incident,
  onCancel,
  onConfirm,
  isPending,
}: {
  incident: AiIncident;
  onCancel: () => void;
  onConfirm: (force: boolean) => void;
  isPending: boolean;
}) {
  const [force, setForce] = useState(false);
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="w-[560px] max-w-full rounded-md bg-white p-6 shadow-xl">
        <h2 className="mb-2 text-lg font-semibold">
          Als Datenpanne eskalieren?
        </h2>
        <p className="text-sm text-muted-foreground">
          Wenn personenbezogene Daten betroffen sind, ist eine Eskalation nach
          DSGVO Art. 33 (72-h-Frist) erforderlich. Die Datenpanne wird mit Daten
          aus dem Vorfall vorausgefüllt.
        </p>
        <div className="my-3 rounded bg-amber-50 p-3 text-xs">
          Vorfall: <strong>{incident.titel}</strong>
        </div>
        <label className="mt-3 flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={force}
            onChange={(e) => setForce(e.target.checked)}
          />
          Ich bestätige, dass personenbezogene Daten betroffen sind (force).
        </label>
        <div className="mt-4 flex justify-end gap-2">
          <Button variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button onClick={() => onConfirm(force)} disabled={isPending}>
            Eskalieren
          </Button>
        </div>
      </div>
    </div>
  );
}
