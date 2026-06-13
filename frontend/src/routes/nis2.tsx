/**
 * NIS2-Selbstbewertung — Betroffenheits-Check + Reife-Score.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  type BetroffenheitsCheck,
  type KontrollAntwort,
  getBetroffenheit,
  getReifeScore,
  listKontrollen,
  saveBetroffenheit,
  updateKontrolle,
} from "@/lib/api/nis2";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";

const SEKTOR_OPTIONS = [
  "energie",
  "verkehr",
  "bank",
  "gesundheit",
  "trinkwasser",
  "abwasser",
  "digital_infra",
  "oeff_verw",
  "raumfahrt",
  "post_kurier",
  "abfall",
  "chemie",
  "lebensmittel",
  "industrie",
  "digital_dienste",
  "forschung",
  "sonstiges",
];

const REIFE_LABEL = [
  "nicht etabliert",
  "initial",
  "geplant",
  "umgesetzt",
  "optimiert",
];

export function NIS2Page() {
  const qc = useQueryClient();
  const betQ = useQuery({ queryKey: ["nis2-bet"], queryFn: getBetroffenheit });
  const kontrollenQ = useQuery({
    queryKey: ["nis2-kontrollen"],
    queryFn: listKontrollen,
  });
  const scoreQ = useQuery({ queryKey: ["nis2-score"], queryFn: getReifeScore });
  const bet = betQ.data;
  const kontrollen = kontrollenQ.data;
  const score = scoreQ.data;
  const anyError = betQ.isError || kontrollenQ.isError || scoreQ.isError;

  const [form, setForm] = useState<Partial<BetroffenheitsCheck>>({});

  // Formular nur EINMAL aus den Server-Daten seeden. Sonst überschriebe jeder
  // Hintergrund-Refetch (Window-Refocus, Save-Invalidierung) die laufenden Eingaben.
  const seeded = useRef(false);
  useEffect(() => {
    if (bet && !seeded.current) {
      setForm(bet);
      seeded.current = true;
    }
  }, [bet]);

  const saveMut = useMutation({
    mutationFn: () => saveBetroffenheit(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["nis2-bet"] });
      toast.success("Betroffenheits-Check gespeichert.");
    },
  });

  const updKontrolle = useMutation({
    mutationFn: (vars: {
      id: number;
      reife_stufe: KontrollAntwort["reife_stufe"];
    }) => updateKontrolle(vars.id, { reife_stufe: vars.reife_stufe }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["nis2-kontrollen"] });
      qc.invalidateQueries({ queryKey: ["nis2-score"] });
    },
  });

  return (
    <div className="space-y-4 max-w-4xl">
      {anyError && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Einige NIS2-Daten konnten nicht geladen werden — Anzeige evtl.
          unvollständig. Bitte Seite neu laden.
        </div>
      )}
      <Card>
        <CardHeader>
          <CardTitle>NIS2-Selbstbewertung</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Bewertung der Betroffenheit nach NIS2-Richtlinie (EU 2022/2555) +
            Reife-Score auf Basis von 10 BSI-Grundschutz-orientierten
            Kontrollfragen. Kein Zertifizierungs-Tool — nur Selbst-Einordnung.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid md:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="ma">Mitarbeiter-Anzahl</Label>
              <Input
                id="ma"
                type="number"
                value={form.mitarbeiter_anzahl ?? ""}
                onChange={(e) =>
                  setForm({
                    ...form,
                    mitarbeiter_anzahl:
                      Number.parseInt(e.target.value, 10) || undefined,
                  })
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="umsatz">Jahresumsatz (EUR)</Label>
              <Input
                id="umsatz"
                type="number"
                value={form.jahresumsatz_eur ?? ""}
                onChange={(e) =>
                  setForm({
                    ...form,
                    jahresumsatz_eur:
                      Number.parseInt(e.target.value, 10) || undefined,
                  })
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="sektor">Sektor</Label>
              <select
                id="sektor"
                value={form.sektor ?? ""}
                onChange={(e) => setForm({ ...form, sektor: e.target.value })}
                className="w-full px-3 py-2 border rounded"
              >
                <option value="">— bitte wählen —</option>
                {SEKTOR_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>
            Betroffenheit speichern + klassifizieren
          </Button>
          {bet && (
            <div className="rounded bg-emerald-50 border border-emerald-200 p-3 text-sm">
              <p>
                Aktuelle Einstufung: <strong>{bet.klassifizierung}</strong>
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Reife-Score (10 Kontrollfragen)</CardTitle>
          {score && (
            <p className="text-sm">
              Score: <strong>{score.score}/100</strong> · {score.beantwortet}{" "}
              von {score.gesamt} Fragen beantwortet
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-3">
          {kontrollen?.map((k) => (
            <div key={k.id} className="border rounded p-3">
              <p className="font-medium text-sm">{k.titel}</p>
              <p className="text-sm text-muted-foreground mt-1">
                {k.frage_text}
              </p>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {[0, 1, 2, 3, 4].map((stufe) => (
                  <button
                    key={stufe}
                    type="button"
                    className={`text-xs px-2 py-1 rounded border ${
                      k.reife_stufe === stufe
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background"
                    }`}
                    onClick={() =>
                      updKontrolle.mutate({
                        id: k.id,
                        reife_stufe: stufe as KontrollAntwort["reife_stufe"],
                      })
                    }
                  >
                    {stufe} — {REIFE_LABEL[stufe]}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
