/**
 * AI-Systeme-Liste — KITool-Inventar + AIMS-Registrierung.
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
  RISIKO_AIMS_LABELS,
  createAiSystem,
  listAiSystems,
  updateAiSystem,
  type AiSystemRegistration,
  type RisikoStufeAIMS,
} from "@/lib/api/iso42001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

const RISIKO_VALUES: RisikoStufeAIMS[] = ["niedrig", "mittel", "hoch", "kritisch"];

export function Iso42001AiSystemsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["iso42001-ai-systems"],
    queryFn: listAiSystems,
  });
  const [edit, setEdit] = useState<AiSystemRegistration | null>(null);

  const saveMut = useMutation({
    mutationFn: (vars: {
      id?: number;
      payload: Partial<AiSystemRegistration> & { ki_tool: number };
    }) =>
      vars.id
        ? updateAiSystem(vars.id, vars.payload)
        : createAiSystem(vars.payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-ai-systems"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("AI-System gespeichert.");
      setEdit(null);
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Fehler beim Speichern";
      toast.error(msg);
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">AI-Systeme im AIMS-Scope</h1>
          <p className="text-sm text-muted-foreground">
            Erweitert das KI-Inventar um AIMS-Felder (AI Risk Owner, Bias-Tests, Monitoring,
            Decommissioning).
          </p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Registrierte AI-Systeme</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Lade …</p>}
          {data && data.results.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Noch kein KI-Tool als AI-System registriert. Lege zunächst KI-Tools im{" "}
              <Link to="/ki-inventar" className="underline">
                KI-Inventar
              </Link>{" "}
              an und registriere sie hier.
            </p>
          )}
          {data && data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>KI-Tool</TableHead>
                  <TableHead>Anbieter</TableHead>
                  <TableHead>AIMS-Risiko</TableHead>
                  <TableHead>AI-Act-Risiko</TableHead>
                  <TableHead>Im Scope</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.results.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-medium">{s.ki_tool_name}</TableCell>
                    <TableCell>{s.ki_tool_anbieter}</TableCell>
                    <TableCell>{RISIKO_AIMS_LABELS[s.risiko_aims]}</TableCell>
                    <TableCell>{s.ki_tool_risiko}</TableCell>
                    <TableCell>{s.in_aims_scope ? "Ja" : "Nein"}</TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" onClick={() => setEdit(s)}>
                        Bearbeiten
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {edit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="w-[640px] max-w-full rounded-md bg-white p-6 shadow-xl">
            <h2 className="mb-3 text-lg font-semibold">
              AIMS-Felder — {edit.ki_tool_name}
            </h2>
            <AiSystemEditForm
              initial={edit}
              onCancel={() => setEdit(null)}
              onSave={(payload) =>
                saveMut.mutate({ id: edit.id, payload: { ki_tool: edit.ki_tool, ...payload } })
              }
              isPending={saveMut.isPending}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function AiSystemEditForm({
  initial,
  onCancel,
  onSave,
  isPending,
}: {
  initial: AiSystemRegistration;
  onCancel: () => void;
  onSave: (payload: Partial<AiSystemRegistration>) => void;
  isPending: boolean;
}) {
  const [risiko, setRisiko] = useState<RisikoStufeAIMS>(initial.risiko_aims);
  const [scope, setScope] = useState(initial.in_aims_scope);
  const [trainingsDaten, setTrainingsDaten] = useState(initial.trainings_daten_quelle);
  const [biasTest, setBiasTest] = useState(initial.bias_tests_durchgefuehrt);
  const [biasUrl, setBiasUrl] = useState(initial.bias_tests_dokument_url);
  const [monitoring, setMonitoring] = useState(initial.monitoring_plan);
  const [decommissioning, setDecommissioning] = useState(initial.decommissioning_plan);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSave({
          risiko_aims: risiko,
          in_aims_scope: scope,
          trainings_daten_quelle: trainingsDaten,
          bias_tests_durchgefuehrt: biasTest,
          bias_tests_dokument_url: biasUrl,
          monitoring_plan: monitoring,
          decommissioning_plan: decommissioning,
        });
      }}
      className="space-y-3"
    >
      <div>
        <label className="mb-1 block text-sm">AIMS-Risiko</label>
        <select
          className="w-full rounded border px-3 py-2 text-sm"
          value={risiko}
          onChange={(e) => setRisiko(e.target.value as RisikoStufeAIMS)}
        >
          {RISIKO_VALUES.map((r) => (
            <option key={r} value={r}>
              {RISIKO_AIMS_LABELS[r]}
            </option>
          ))}
        </select>
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={scope}
          onChange={(e) => setScope(e.target.checked)}
        />
        Im AIMS-Scope
      </label>
      <div>
        <label className="mb-1 block text-sm">
          Trainingsdaten-Quelle (A.7.4/A.7.5)
        </label>
        <textarea
          rows={2}
          className="w-full rounded border px-3 py-2 text-sm"
          value={trainingsDaten}
          onChange={(e) => setTrainingsDaten(e.target.value)}
        />
      </div>
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={biasTest}
          onChange={(e) => setBiasTest(e.target.checked)}
        />
        Bias-Tests durchgeführt
      </label>
      {biasTest && (
        <input
          className="w-full rounded border px-3 py-2 text-sm"
          placeholder="Link zum Test-Dokument"
          value={biasUrl}
          onChange={(e) => setBiasUrl(e.target.value)}
        />
      )}
      <div>
        <label className="mb-1 block text-sm">Monitoring-Plan (A.6.2.6)</label>
        <textarea
          rows={2}
          className="w-full rounded border px-3 py-2 text-sm"
          value={monitoring}
          onChange={(e) => setMonitoring(e.target.value)}
        />
      </div>
      <div>
        <label className="mb-1 block text-sm">Decommissioning-Plan (A.6.2.8)</label>
        <textarea
          rows={2}
          className="w-full rounded border px-3 py-2 text-sm"
          value={decommissioning}
          onChange={(e) => setDecommissioning(e.target.value)}
        />
      </div>
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Abbrechen
        </Button>
        <Button type="submit" disabled={isPending}>
          Speichern
        </Button>
      </div>
    </form>
  );
}
