/**
 * GBU-Wizard — 4-Step-Form für Anlage / Edit einer Gefährdungsbeurteilung.
 *
 * Routes:
 *   - /arbeitsschutz/gbu/neu          → Create-Modus
 *   - /arbeitsschutz/gbu/:id/bearbeiten → Edit-Modus (lädt bestehende GBU)
 *
 * Pragmatisch: Single-Page mit visuell getrennten Sektionen + interner
 * Schritt-Navigation (TabsList-Pattern via Buttons). Schritte können
 * frei angesprungen werden, sobald GBU einmal angelegt ist (Step 2-4
 * brauchen eine GBU-ID, weil Positionen + LLM-Vorschlag pro-GBU
 * persistiert werden müssen).
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useMitarbeiterList } from "@/lib/api/mitarbeiter";
import {
  akzeptierenVorschlag,
  createGbu,
  createGbuPosition,
  deleteGbuPosition,
  freigebenGbu,
  getGbu,
  listGefaehrdungen,
  listTaetigkeiten,
  suggestGefaehrdungen,
  updateGbu,
  updateGbuPosition,
  type Gefaehrdung,
  type GbuPosition,
  type GbuVorschlag,
  type Taetigkeit,
} from "@/lib/api/arbeitsschutz";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";

type Step = 1 | 2 | 3 | 4;

const STEP_LABELS: Record<Step, string> = {
  1: "1. Tätigkeit",
  2: "2. Gefährdungen",
  3: "3. Risiko bewerten",
  4: "4. Zusammenfassung",
};

export function GbuWizardPage() {
  const params = useParams<{ id?: string }>();
  const editId = params.id ? Number(params.id) : null;
  const navigate = useNavigate();
  const qc = useQueryClient();

  // Schritt-State
  const [step, setStep] = useState<Step>(1);

  // GBU-State (Step 1)
  const [titel, setTitel] = useState("");
  const [taetigkeitId, setTaetigkeitId] = useState<number | "">("");
  const [verantwortlicher, setVerantwortlicher] = useState<number | "">("");
  const [bemerkung, setBemerkung] = useState("");
  const [gbuId, setGbuId] = useState<number | null>(editId);

  // LLM-Vorschlag-State (Step 2)
  const [vorschlag, setVorschlag] = useState<GbuVorschlag | null>(null);

  // --- Queries ---
  const taetigkeiten = useQuery({
    queryKey: ["as-taetigkeiten"],
    queryFn: listTaetigkeiten,
  });
  const gefaehrdungen = useQuery({
    queryKey: ["as-gefaehrdungen"],
    queryFn: listGefaehrdungen,
  });
  const mitarbeiter = useMitarbeiterList();

  const gbuQuery = useQuery({
    queryKey: ["as-gbu", gbuId],
    queryFn: () => getGbu(gbuId as number),
    enabled: gbuId !== null,
  });

  // Edit-Modus: Pre-fill aus geladener GBU (einmalig)
  useEffect(() => {
    if (editId && gbuQuery.data && titel === "") {
      setTitel(gbuQuery.data.titel);
      setTaetigkeitId(gbuQuery.data.taetigkeit);
      setVerantwortlicher(gbuQuery.data.verantwortlicher ?? "");
      setBemerkung(gbuQuery.data.bemerkung ?? "");
    }
  }, [editId, gbuQuery.data, titel]);

  const positionen: GbuPosition[] = gbuQuery.data?.positionen ?? [];

  // --- Mutations ---
  const createMut = useMutation({
    mutationFn: createGbu,
    onSuccess: (gbu) => {
      setGbuId(gbu.id);
      qc.invalidateQueries({ queryKey: ["as-gbu"] });
      toast.success("GBU angelegt.");
      setStep(2);
    },
    onError: () => toast.error("Anlegen fehlgeschlagen."),
  });

  const updateMut = useMutation({
    mutationFn: (payload: Parameters<typeof updateGbu>[1]) =>
      updateGbu(gbuId as number, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["as-gbu", gbuId] });
      qc.invalidateQueries({ queryKey: ["as-gbu"] });
      toast.success("Gespeichert.");
    },
    onError: () => toast.error("Speichern fehlgeschlagen."),
  });

  const addPosMut = useMutation({
    mutationFn: createGbuPosition,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["as-gbu", gbuId] }),
    onError: () => toast.error("Gefährdung konnte nicht hinzugefügt werden."),
  });

  const delPosMut = useMutation({
    mutationFn: deleteGbuPosition,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["as-gbu", gbuId] }),
  });

  const updatePosMut = useMutation({
    mutationFn: (vars: {
      id: number;
      data: Parameters<typeof updateGbuPosition>[1];
    }) => updateGbuPosition(vars.id, vars.data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["as-gbu", gbuId] }),
  });

  const suggestMut = useMutation({
    mutationFn: () => suggestGefaehrdungen(gbuId as number),
    onSuccess: (v) => {
      setVorschlag(v);
      toast.success("LLM-Vorschlag geladen — Vorschläge prüfen!");
    },
    onError: () => toast.error("LLM-Vorschlag fehlgeschlagen."),
  });

  const akzeptMut = useMutation({
    mutationFn: (codes: string[] | undefined) =>
      akzeptierenVorschlag(vorschlag!.id, codes),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["as-gbu", gbuId] });
      let msg = `${res.created} Gefährdungen übernommen.`;
      if (res.skipped_unknown_codes.length) {
        msg += ` ${res.skipped_unknown_codes.length} unbekannt: ${res.skipped_unknown_codes.join(", ")}.`;
      }
      toast.success(msg);
      setVorschlag(null);
    },
    onError: () => toast.error("Übernahme fehlgeschlagen."),
  });

  const freigebenMut = useMutation({
    mutationFn: () => freigebenGbu(gbuId as number),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["as-gbu", gbuId] });
      qc.invalidateQueries({ queryKey: ["as-gbu"] });
      toast.success("GBU freigegeben.");
      navigate("/arbeitsschutz/gbu");
    },
    onError: () => toast.error("Freigabe fehlgeschlagen."),
  });

  const selectedTaetigkeit: Taetigkeit | undefined = taetigkeiten.data?.results.find(
    (t) => t.id === taetigkeitId,
  );

  // --- Step 1: Tätigkeit + Titel ---
  function handleStep1Submit(e: React.FormEvent) {
    e.preventDefault();
    if (!titel || taetigkeitId === "") {
      toast.error("Titel und Tätigkeit sind Pflicht.");
      return;
    }
    if (gbuId === null) {
      createMut.mutate({
        titel,
        taetigkeit: Number(taetigkeitId),
        verantwortlicher: verantwortlicher === "" ? null : Number(verantwortlicher),
        bemerkung,
      });
    } else {
      updateMut.mutate({
        titel,
        taetigkeit: Number(taetigkeitId),
        verantwortlicher: verantwortlicher === "" ? null : Number(verantwortlicher),
        bemerkung,
      });
      setStep(2);
    }
  }

  const canAdvance = gbuId !== null;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">
            {editId ? "GBU bearbeiten" : "Neue Gefährdungsbeurteilung"}
          </h1>
          <p className="text-sm text-muted-foreground">
            ArbSchG §5 — eine GBU pro Tätigkeit. Wirksamkeitsprüfung jährlich.
          </p>
        </div>
        <Button variant="outline" onClick={() => navigate("/arbeitsschutz/gbu")}>
          Abbrechen
        </Button>
      </div>

      {/* Schritt-Navigation */}
      <div className="flex gap-2 border-b">
        {([1, 2, 3, 4] as Step[]).map((s) => (
          <button
            key={s}
            type="button"
            disabled={s !== 1 && !canAdvance}
            onClick={() => setStep(s)}
            className={
              "px-4 py-2 text-sm font-medium border-b-2 -mb-px " +
              (step === s
                ? "border-emerald-600 text-emerald-700"
                : "border-transparent text-muted-foreground hover:text-foreground") +
              (s !== 1 && !canAdvance ? " opacity-40 cursor-not-allowed" : "")
            }
          >
            {STEP_LABELS[s]}
          </button>
        ))}
      </div>

      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Tätigkeit auswählen</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={handleStep1Submit}>
              <div>
                <Label>Titel der GBU</Label>
                <Input
                  value={titel}
                  onChange={(e) => setTitel(e.target.value)}
                  placeholder='z. B. "GBU CNC-Fräsen Werkstatt 2"'
                  required
                />
              </div>
              <div>
                <Label>Tätigkeit</Label>
                <select
                  className="w-full rounded border px-3 py-2 text-sm"
                  value={taetigkeitId}
                  onChange={(e) =>
                    setTaetigkeitId(e.target.value ? Number(e.target.value) : "")
                  }
                  required
                >
                  <option value="">— bitte wählen —</option>
                  {taetigkeiten.data?.results.map((t) => (
                    <option key={t.id} value={t.id}>
                      {t.arbeitsbereich_name
                        ? `${t.arbeitsbereich_name} · ${t.name}`
                        : t.name}
                    </option>
                  ))}
                </select>
                {selectedTaetigkeit?.arbeitsbereich_name && (
                  <p className="mt-1 text-xs text-muted-foreground">
                    Arbeitsbereich:{" "}
                    <strong>{selectedTaetigkeit.arbeitsbereich_name}</strong>
                    {selectedTaetigkeit.beschreibung && (
                      <> · {selectedTaetigkeit.beschreibung}</>
                    )}
                  </p>
                )}
              </div>
              <div>
                <Label>Verantwortlicher (optional)</Label>
                <select
                  className="w-full rounded border px-3 py-2 text-sm"
                  value={verantwortlicher}
                  onChange={(e) =>
                    setVerantwortlicher(e.target.value ? Number(e.target.value) : "")
                  }
                >
                  <option value="">— später festlegen —</option>
                  {mitarbeiter.data?.results.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.vorname} {m.nachname} ({m.rolle || "—"})
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <Label>Bemerkung (optional)</Label>
                <textarea
                  className="w-full rounded border px-3 py-2 text-sm"
                  rows={3}
                  value={bemerkung}
                  onChange={(e) => setBemerkung(e.target.value)}
                />
              </div>
              <div className="flex justify-end gap-2">
                <Button
                  type="submit"
                  disabled={createMut.isPending || updateMut.isPending}
                >
                  {gbuId === null ? "Anlegen & weiter" : "Speichern & weiter"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {step === 2 && (
        <Step2Gefaehrdungen
          gefaehrdungen={gefaehrdungen.data?.results ?? []}
          positionen={positionen}
          onAdd={(gefId) =>
            addPosMut.mutate({
              gbu: gbuId as number,
              gefaehrdung: gefId,
              wahrscheinlichkeit: 2,
              schwere: 2,
              relevant: true,
            })
          }
          onRemove={(posId) => delPosMut.mutate(posId)}
          vorschlag={vorschlag}
          onSuggest={() => suggestMut.mutate()}
          onAccept={(codes) => akzeptMut.mutate(codes)}
          suggestPending={suggestMut.isPending}
          acceptPending={akzeptMut.isPending}
          onContinue={() => setStep(3)}
        />
      )}

      {step === 3 && (
        <Step3RisikoBewertung
          positionen={positionen}
          onUpdate={(posId, data) => updatePosMut.mutate({ id: posId, data })}
          onContinue={() => setStep(4)}
        />
      )}

      {step === 4 && (
        <Step4Zusammenfassung
          titel={titel}
          taetigkeit={selectedTaetigkeit}
          positionen={positionen}
          verantwortlicher={verantwortlicher}
          mitarbeiter={mitarbeiter.data?.results ?? []}
          onVerantwortlicherChange={(v) => setVerantwortlicher(v)}
          onSaveEntwurf={() => {
            updateMut.mutate({
              verantwortlicher:
                verantwortlicher === "" ? null : Number(verantwortlicher),
              status: "entwurf",
            });
            navigate("/arbeitsschutz/gbu");
          }}
          onFreigeben={() => {
            // Verantwortlicher noch speichern, dann freigeben
            if (verantwortlicher !== "") {
              updateMut.mutate({ verantwortlicher: Number(verantwortlicher) });
            }
            freigebenMut.mutate();
          }}
          freigebenPending={freigebenMut.isPending}
        />
      )}
    </div>
  );
}

// =========================================================================
// Step 2 — Gefährdungen identifizieren
// =========================================================================

function Step2Gefaehrdungen({
  gefaehrdungen,
  positionen,
  onAdd,
  onRemove,
  vorschlag,
  onSuggest,
  onAccept,
  suggestPending,
  acceptPending,
  onContinue,
}: {
  gefaehrdungen: Gefaehrdung[];
  positionen: GbuPosition[];
  onAdd: (id: number) => void;
  onRemove: (posId: number) => void;
  vorschlag: GbuVorschlag | null;
  onSuggest: () => void;
  onAccept: (codes?: string[]) => void;
  suggestPending: boolean;
  acceptPending: boolean;
  onContinue: () => void;
}) {
  const [search, setSearch] = useState("");

  const selectedGefIds = new Set(positionen.map((p) => p.gefaehrdung));
  const filtered = gefaehrdungen.filter((g) => {
    if (!search) return true;
    const q = search.toLowerCase();
    return (
      g.name.toLowerCase().includes(q) ||
      g.code.toLowerCase().includes(q) ||
      g.kategorie.toLowerCase().includes(q)
    );
  });

  const byKategorie = filtered.reduce<Record<string, Gefaehrdung[]>>((acc, g) => {
    const k = g.kategorie || "Sonstige";
    if (!acc[k]) acc[k] = [];
    acc[k].push(g);
    return acc;
  }, {});

  const sortedKategorien = Object.keys(byKategorie).sort();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Gefährdungen identifizieren</CardTitle>
        <p className="text-sm text-muted-foreground">
          Aus dem Katalog auswählen oder LLM-Vorschlag nutzen. Mehrfachauswahl
          möglich.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="Suchen (Code, Name, Kategorie)…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Button
            type="button"
            variant="outline"
            onClick={onSuggest}
            disabled={suggestPending}
          >
            {suggestPending ? "lädt…" : "LLM-Vorschlag holen"}
          </Button>
        </div>

        {vorschlag && (
          <div className="rounded border border-amber-300 bg-amber-50 p-4 text-sm">
            <p className="font-semibold text-amber-900">
              LLM-Vorschlag — bitte vor Übernahme prüfen
            </p>
            <p className="mt-1 text-xs text-amber-800">
              Vorschlag ohne rechtliche Bewertung. Quelle: {vorschlag.quelle}{" "}
              {vorschlag.llm_modell && <>· {vorschlag.llm_modell}</>}
            </p>
            <p className="mt-2 text-amber-900">{vorschlag.begruendung}</p>
            <ul className="mt-2 list-disc pl-5 text-amber-900">
              {vorschlag.vorgeschlagene_codes.map((c) => (
                <li key={c.code}>
                  <code className="font-mono">{c.code}</code>
                </li>
              ))}
            </ul>
            <div className="mt-3 flex gap-2">
              <Button
                type="button"
                size="sm"
                onClick={() => onAccept(undefined)}
                disabled={acceptPending}
              >
                Alle übernehmen
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => onAccept([])}
                disabled={acceptPending}
              >
                Schließen
              </Button>
            </div>
          </div>
        )}

        <div>
          <p className="mb-2 text-sm font-semibold">
            Ausgewählte Gefährdungen ({positionen.length})
          </p>
          {positionen.length === 0 && (
            <p className="text-xs text-muted-foreground">
              Noch keine Gefährdung ausgewählt.
            </p>
          )}
          {positionen.length > 0 && (
            <ul className="space-y-1">
              {positionen.map((p) => (
                <li
                  key={p.id}
                  className="flex items-center justify-between rounded bg-slate-50 px-3 py-2 text-sm"
                >
                  <span>
                    <code className="mr-2 font-mono text-xs">{p.gefaehrdung_code}</code>
                    {p.gefaehrdung_name}
                  </span>
                  <button
                    type="button"
                    className="text-xs text-rose-700 underline"
                    onClick={() => onRemove(p.id)}
                  >
                    Entfernen
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="max-h-96 overflow-y-auto rounded border p-2">
          {sortedKategorien.map((k) => (
            <div key={k} className="mb-3">
              <p className="mb-1 text-xs font-semibold uppercase text-muted-foreground">
                {k}
              </p>
              <ul className="space-y-1">
                {byKategorie[k].map((g) => {
                  const isSelected = selectedGefIds.has(g.id);
                  return (
                    <li key={g.id} className="text-sm">
                      <button
                        type="button"
                        disabled={isSelected}
                        onClick={() => onAdd(g.id)}
                        className={
                          "w-full rounded px-2 py-1 text-left " +
                          (isSelected
                            ? "bg-emerald-50 text-emerald-800 cursor-default"
                            : "hover:bg-slate-100")
                        }
                      >
                        <code className="mr-2 font-mono text-xs">{g.code}</code>
                        {g.name}
                        {isSelected && (
                          <span className="ml-2 text-xs">✓ ausgewählt</span>
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>

        <div className="flex justify-end">
          <Button
            type="button"
            onClick={onContinue}
            disabled={positionen.length === 0}
          >
            Weiter zur Risiko-Bewertung
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// =========================================================================
// Step 3 — Risiko bewerten (5x5 Heatmap)
// =========================================================================

function riskColor(score: number): string {
  if (score <= 6) return "bg-emerald-200 text-emerald-900";
  if (score <= 15) return "bg-amber-200 text-amber-900";
  return "bg-rose-300 text-rose-900";
}

function Step3RisikoBewertung({
  positionen,
  onUpdate,
  onContinue,
}: {
  positionen: GbuPosition[];
  onUpdate: (
    posId: number,
    data: { wahrscheinlichkeit?: number; schwere?: number },
  ) => void;
  onContinue: () => void;
}) {
  // Bubble-Index: für jede (w,s)-Zelle die Liste der Positionen
  const bubbleMap = new Map<string, GbuPosition[]>();
  for (const p of positionen) {
    const key = `${p.wahrscheinlichkeit}-${p.schwere}`;
    const arr = bubbleMap.get(key) ?? [];
    arr.push(p);
    bubbleMap.set(key, arr);
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Risiko bewerten</CardTitle>
        <p className="text-sm text-muted-foreground">
          Pro Gefährdung: Eintrittswahrscheinlichkeit (W) und Schadensschwere (S)
          von 1–5. Risiko-Score = W × S.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Heatmap */}
        <div>
          <p className="mb-2 text-sm font-semibold">5×5-Risiko-Matrix</p>
          <div className="inline-block">
            <div className="grid grid-cols-[auto_repeat(5,minmax(56px,1fr))] gap-1">
              <div></div>
              {[1, 2, 3, 4, 5].map((s) => (
                <div
                  key={`h-${s}`}
                  className="text-center text-xs font-medium text-muted-foreground"
                >
                  S{s}
                </div>
              ))}
              {[5, 4, 3, 2, 1].flatMap((w) => [
                <div
                  key={`w-${w}`}
                  className="text-right pr-2 text-xs font-medium text-muted-foreground"
                >
                  W{w}
                </div>,
                ...[1, 2, 3, 4, 5].map((s) => {
                  const score = w * s;
                  const cellPositions = bubbleMap.get(`${w}-${s}`) ?? [];
                  return (
                    <div
                      key={`c-${w}-${s}`}
                      className={
                        "h-14 rounded flex flex-col items-center justify-center text-xs relative " +
                        riskColor(score)
                      }
                      title={`W=${w} · S=${s} · Score=${score}`}
                    >
                      <span className="font-semibold">{score}</span>
                      {cellPositions.length > 0 && (
                        <span
                          className="absolute -top-1 -right-1 inline-flex h-5 min-w-[1.25rem] items-center justify-center rounded-full bg-slate-900 px-1 text-[10px] font-bold text-white"
                          title={cellPositions
                            .map((p) => p.gefaehrdung_name)
                            .join(", ")}
                        >
                          {cellPositions.length}
                        </span>
                      )}
                    </div>
                  );
                }),
              ])}
            </div>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Grün: 1–6 (gering) · Gelb: 7–15 (mittel) · Rot: 16–25 (hoch/sehr hoch)
          </p>
        </div>

        {/* Pro-Position-Slider */}
        <div className="space-y-3">
          <p className="text-sm font-semibold">Bewertung je Gefährdung</p>
          {positionen.map((p) => (
            <div key={p.id} className="rounded border p-3">
              <div className="mb-2 flex items-center justify-between">
                <div>
                  <code className="mr-2 font-mono text-xs">{p.gefaehrdung_code}</code>
                  <span className="text-sm font-medium">{p.gefaehrdung_name}</span>
                </div>
                <div
                  className={
                    "rounded px-2 py-1 text-xs font-semibold " +
                    riskColor(p.risiko_score)
                  }
                >
                  {p.risiko_score} · {p.risiko_klasse}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs">
                    Wahrscheinlichkeit: <strong>{p.wahrscheinlichkeit}</strong>
                  </Label>
                  <input
                    type="range"
                    min={1}
                    max={5}
                    step={1}
                    value={p.wahrscheinlichkeit}
                    onChange={(e) =>
                      onUpdate(p.id, { wahrscheinlichkeit: Number(e.target.value) })
                    }
                    className="w-full"
                  />
                </div>
                <div>
                  <Label className="text-xs">
                    Schadensschwere: <strong>{p.schwere}</strong>
                  </Label>
                  <input
                    type="range"
                    min={1}
                    max={5}
                    step={1}
                    value={p.schwere}
                    onChange={(e) =>
                      onUpdate(p.id, { schwere: Number(e.target.value) })
                    }
                    className="w-full"
                  />
                </div>
              </div>
            </div>
          ))}
          {positionen.length === 0 && (
            <p className="text-xs text-muted-foreground">
              Keine Gefährdungen ausgewählt — zurück zu Schritt 2.
            </p>
          )}
        </div>

        <div className="flex justify-end">
          <Button type="button" onClick={onContinue}>
            Weiter zur Zusammenfassung
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

// =========================================================================
// Step 4 — Zusammenfassung + Freigabe
// =========================================================================

function Step4Zusammenfassung({
  titel,
  taetigkeit,
  positionen,
  verantwortlicher,
  mitarbeiter,
  onVerantwortlicherChange,
  onSaveEntwurf,
  onFreigeben,
  freigebenPending,
}: {
  titel: string;
  taetigkeit?: Taetigkeit;
  positionen: GbuPosition[];
  verantwortlicher: number | "";
  mitarbeiter: Array<{ id: number; vorname: string; nachname: string; rolle: string }>;
  onVerantwortlicherChange: (v: number | "") => void;
  onSaveEntwurf: () => void;
  onFreigeben: () => void;
  freigebenPending: boolean;
}) {
  const maxScore = positionen.reduce((max, p) => Math.max(max, p.risiko_score), 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Zusammenfassung & Freigabe</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded bg-slate-50 p-4 text-sm">
          <p>
            <strong>Titel:</strong> {titel}
          </p>
          <p>
            <strong>Tätigkeit:</strong>{" "}
            {taetigkeit
              ? `${taetigkeit.arbeitsbereich_name ?? "—"} · ${taetigkeit.name}`
              : "—"}
          </p>
          <p>
            <strong>Anzahl Gefährdungen:</strong> {positionen.length}
          </p>
          <p>
            <strong>Höchster Risiko-Score:</strong>{" "}
            <span
              className={
                "inline-block rounded px-2 py-0.5 font-semibold " +
                riskColor(maxScore)
              }
            >
              {maxScore || "—"}
            </span>
          </p>
        </div>

        <div>
          <Label>Verantwortlicher</Label>
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={verantwortlicher}
            onChange={(e) =>
              onVerantwortlicherChange(e.target.value ? Number(e.target.value) : "")
            }
          >
            <option value="">— keiner zugewiesen —</option>
            {mitarbeiter.map((m) => (
              <option key={m.id} value={m.id}>
                {m.vorname} {m.nachname} ({m.rolle || "—"})
              </option>
            ))}
          </select>
        </div>

        <div>
          <p className="mb-2 text-sm font-semibold">Bewertete Gefährdungen</p>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b text-left text-xs text-muted-foreground">
                <th className="py-1">Code</th>
                <th className="py-1">Bezeichnung</th>
                <th className="py-1">W</th>
                <th className="py-1">S</th>
                <th className="py-1">Score</th>
                <th className="py-1">Klasse</th>
              </tr>
            </thead>
            <tbody>
              {positionen.map((p) => (
                <tr key={p.id} className="border-b">
                  <td className="py-1 font-mono text-xs">{p.gefaehrdung_code}</td>
                  <td className="py-1">{p.gefaehrdung_name}</td>
                  <td className="py-1">{p.wahrscheinlichkeit}</td>
                  <td className="py-1">{p.schwere}</td>
                  <td className="py-1">
                    <span
                      className={
                        "rounded px-2 py-0.5 text-xs font-semibold " +
                        riskColor(p.risiko_score)
                      }
                    >
                      {p.risiko_score}
                    </span>
                  </td>
                  <td className="py-1">{p.risiko_klasse}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="rounded bg-amber-50 p-3 text-xs text-amber-900">
          Freigabe ist verbindlich. Eine freigegebene GBU kann später durch eine
          überarbeitete Version (neue Revision) ersetzt werden, der ursprüngliche
          Stand bleibt in der Historie.
        </div>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onSaveEntwurf}>
            Als Entwurf speichern
          </Button>
          <Button
            type="button"
            onClick={onFreigeben}
            disabled={freigebenPending || positionen.length === 0}
          >
            {freigebenPending ? "lädt…" : "Freigeben"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
