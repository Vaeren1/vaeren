/**
 * Vorschlag-Review (Slice 3). Zeigt offene LLM-Vorschlaege fuer einen
 * Kurs. Jeder Vorschlag hat 3 Aktionen: Akzeptieren / Inline-Editieren+Akzeptieren
 * / Verwerfen. RDG-Layer-3-Gate: kein Bulk-Akzeptieren.
 */
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  type FrageVorschlag,
  useAkzeptiereVorschlag,
  useVerwerfeVorschlag,
  useVorschlaege,
} from "@/lib/api/schulungen";
import { Check, Pencil, Sparkles, X } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function VorschlagReview({ kursId }: { kursId: number }) {
  const { data, isLoading } = useVorschlaege(kursId);
  const list = Array.isArray(data) ? data : (data?.results ?? []);
  const offen = list.filter((v) => v.status === "offen");

  if (isLoading || offen.length === 0) return null;

  return (
    <div className="space-y-2 rounded border border-amber-200 bg-amber-50/40 p-3">
      <div className="flex items-center gap-2 text-sm font-medium text-amber-900">
        <Sparkles className="h-4 w-4" />
        {offen.length} LLM-Vorschläge warten auf Review
      </div>
      <p className="text-xs text-amber-900">
        Vorschläge sind LLM-generiert. Sie prüfen jeden Vorschlag, bevor er
        produktiv wird (RDG-Layer-3).
      </p>
      <div className="space-y-2">
        {offen.map((v) => (
          <VorschlagCard key={v.id} vorschlag={v} kursId={kursId} />
        ))}
      </div>
    </div>
  );
}

function VorschlagCard({
  vorschlag,
  kursId,
}: {
  vorschlag: FrageVorschlag;
  kursId: number;
}) {
  const [editing, setEditing] = useState(false);
  const [text, setText] = useState(vorschlag.text);
  const [erklaerung, setErklaerung] = useState(vorschlag.erklaerung);
  const [optionen, setOptionen] = useState(vorschlag.optionen);
  const akzeptieren = useAkzeptiereVorschlag();
  const verwerfen = useVerwerfeVorschlag();

  const setKorrekt = (i: number) =>
    setOptionen((prev) =>
      prev.map((o, idx) => ({ ...o, ist_korrekt: idx === i })),
    );
  const updateOpt = (i: number, t: string) =>
    setOptionen((prev) =>
      prev.map((o, idx) => (idx === i ? { ...o, text: t } : o)),
    );

  const onAccept = (useEdits: boolean) => {
    akzeptieren.mutate(
      {
        id: vorschlag.id,
        kursId,
        payload: useEdits ? { text, erklaerung, optionen } : undefined,
      },
      {
        onSuccess: () => toast.success("Vorschlag akzeptiert → Frage angelegt."),
        onError: (e) => toast.error(`Fehler: ${e.message}`),
      },
    );
  };
  const onReject = () => {
    verwerfen.mutate(
      { id: vorschlag.id, kursId },
      {
        onSuccess: () => toast.success("Verworfen."),
        onError: (e) => toast.error(`Fehler: ${e.message}`),
      },
    );
  };

  return (
    <div className="rounded border bg-card p-3">
      {editing ? (
        <div className="space-y-2">
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={2}
            className="w-full rounded border border-input bg-background p-2 text-sm"
          />
          <div className="space-y-1">
            {optionen.map((o, i) => (
              <div key={i} className="flex items-center gap-2">
                <input
                  type="radio"
                  checked={o.ist_korrekt}
                  onChange={() => setKorrekt(i)}
                />
                <Input
                  value={o.text}
                  onChange={(e) => updateOpt(i, e.target.value)}
                />
              </div>
            ))}
          </div>
          <textarea
            value={erklaerung}
            onChange={(e) => setErklaerung(e.target.value)}
            rows={2}
            placeholder="Erklärung"
            className="w-full rounded border border-input bg-background p-2 text-sm"
          />
        </div>
      ) : (
        <div>
          <p className="font-medium">{vorschlag.text}</p>
          <ul className="mt-2 space-y-0.5 text-sm">
            {vorschlag.optionen.map((o, i) => (
              <li
                key={i}
                className={
                  o.ist_korrekt
                    ? "rounded bg-emerald-50 px-2 py-0.5 text-emerald-900"
                    : "px-2 py-0.5 text-slate-700"
                }
              >
                {o.ist_korrekt ? "✓ " : "○ "}
                {o.text}
              </li>
            ))}
          </ul>
          {vorschlag.erklaerung && (
            <p className="mt-2 text-xs italic text-muted-foreground">
              Erklärung: {vorschlag.erklaerung}
            </p>
          )}
        </div>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-1 text-xs text-muted-foreground">
        <span className="rounded bg-slate-100 px-1.5 py-0.5">
          {vorschlag.llm_modell}
        </span>
        {!editing ? (
          <Button
            size="sm"
            variant="ghost"
            className="ml-auto"
            onClick={() => setEditing(true)}
          >
            <Pencil className="mr-1 h-3 w-3" /> Bearbeiten
          </Button>
        ) : null}
        <div className={editing ? "ml-auto flex gap-1" : "flex gap-1"}>
          {editing && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => setEditing(false)}
            >
              Abbrechen
            </Button>
          )}
          <Button
            size="sm"
            onClick={() => onAccept(editing)}
            disabled={akzeptieren.isPending}
          >
            <Check className="mr-1 h-3 w-3" />
            {editing ? "Speichern + Akzeptieren" : "Akzeptieren"}
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={onReject}
            disabled={verwerfen.isPending}
          >
            <X className="mr-1 h-3 w-3" /> Verwerfen
          </Button>
        </div>
      </div>
    </div>
  );
}
