/**
 * Quiz-Pool-Editor (Slice 3). Manuelles Anlegen/Editieren von Fragen,
 * Auflistung bestehender, plus „Vorschlaege generieren"-Trigger.
 *
 * Vorschlag-Review-Karten leben in einer eigenen Komponente, weil sie
 * unabhaengig sichtbar sein duerfen (auch nach Schliessen des Editors).
 */
import { VorschlagReview } from "@/components/kurs/vorschlag-review";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  type AntwortOptionInput,
  type Frage,
  type FrageInput,
  useCreateFrage,
  useDeleteFrage,
  useGenerateVorschlaege,
  useUpdateFrage,
} from "@/lib/api/schulungen";
import { Loader2, Pencil, Plus, Sparkles, Trash2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

export function QuizEditor({
  kursId,
  fragen,
  readonly = false,
}: {
  kursId: number;
  fragen: Frage[];
  readonly?: boolean;
}) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const del = useDeleteFrage();
  const generate = useGenerateVorschlaege();

  const handleDelete = (id: number, text: string) => {
    if (!window.confirm(`Frage „${text.slice(0, 60)}" wirklich löschen?`)) return;
    del.mutate(
      { id, kursId },
      {
        onSuccess: () => toast.success("Frage gelöscht."),
        onError: () => toast.error("Löschen fehlgeschlagen."),
      },
    );
  };

  const handleGenerate = () => {
    if (
      !window.confirm(
        "LLM generiert 10 Vorschläge aus den Modul-Texten. Jeder Vorschlag muss manuell bestätigt werden. Fortfahren?",
      )
    ) {
      return;
    }
    generate.mutate(
      { kurs: kursId, anzahl: 10 },
      {
        onSuccess: () =>
          toast.success("Generierung läuft — Vorschläge erscheinen unten in 30–90 Sek."),
        onError: (e) => toast.error(`Konnte nicht starten: ${e.message}`),
      },
    );
  };

  return (
    <div className="space-y-4">
      <VorschlagReview kursId={kursId} />

      <div className="space-y-2">
        {fragen.map((f, idx) =>
          editingId === f.id ? (
            <FrageFormCard
              key={f.id}
              kursId={kursId}
              existing={f}
              onClose={() => setEditingId(null)}
            />
          ) : (
            <FrageRow
              key={f.id}
              frage={f}
              index={idx + 1}
              readonly={readonly}
              onEdit={() => setEditingId(f.id)}
              onDelete={() => handleDelete(f.id, f.text)}
            />
          ),
        )}
      </div>

      {!readonly &&
        (showCreate ? (
          <FrageFormCard
            kursId={kursId}
            newOrder={fragen.length}
            onClose={() => setShowCreate(false)}
          />
        ) : (
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" onClick={() => setShowCreate(true)}>
              <Plus className="mr-1 h-4 w-4" /> Frage manuell anlegen
            </Button>
            <Button
              variant="outline"
              onClick={handleGenerate}
              disabled={generate.isPending}
            >
              {generate.isPending ? (
                <Loader2 className="mr-1 h-4 w-4 animate-spin" />
              ) : (
                <Sparkles className="mr-1 h-4 w-4" />
              )}
              Vorschläge aus Material generieren
            </Button>
          </div>
        ))}
    </div>
  );
}

function FrageRow({
  frage,
  index,
  readonly,
  onEdit,
  onDelete,
}: {
  frage: Frage;
  index: number;
  readonly: boolean;
  onEdit: () => void;
  onDelete: () => void;
}) {
  return (
    <div className="rounded border bg-card p-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1">
          <div className="text-xs uppercase tracking-wide text-muted-foreground">
            Frage {index}
          </div>
          <p className="font-medium">{frage.text}</p>
          <ul className="mt-2 space-y-0.5 text-sm">
            {frage.optionen.map((o) => (
              <li
                key={o.id}
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
          {frage.erklaerung && (
            <p className="mt-2 text-xs italic text-muted-foreground">
              Erklärung: {frage.erklaerung}
            </p>
          )}
        </div>
        {!readonly && (
          <div className="flex gap-1">
            <Button size="icon" variant="ghost" onClick={onEdit}>
              <Pencil className="h-4 w-4" />
            </Button>
            <Button size="icon" variant="ghost" onClick={onDelete}>
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

function FrageFormCard({
  kursId,
  existing,
  newOrder,
  onClose,
}: {
  kursId: number;
  existing?: Frage;
  newOrder?: number;
  onClose: () => void;
}) {
  const [text, setText] = useState(existing?.text ?? "");
  const [erklaerung, setErklaerung] = useState(existing?.erklaerung ?? "");
  const [optionen, setOptionen] = useState<AntwortOptionInput[]>(
    existing?.optionen?.length
      ? existing.optionen.map((o) => ({
          text: o.text,
          ist_korrekt: o.ist_korrekt,
          reihenfolge: o.reihenfolge,
        }))
      : [
          { text: "", ist_korrekt: true, reihenfolge: 0 },
          { text: "", ist_korrekt: false, reihenfolge: 1 },
          { text: "", ist_korrekt: false, reihenfolge: 2 },
          { text: "", ist_korrekt: false, reihenfolge: 3 },
        ],
  );
  const create = useCreateFrage();
  const update = useUpdateFrage();

  const updateOption = (i: number, patch: Partial<AntwortOptionInput>) => {
    setOptionen((prev) =>
      prev.map((o, idx) => (idx === i ? { ...o, ...patch } : o)),
    );
  };
  const setKorrekt = (i: number) => {
    setOptionen((prev) =>
      prev.map((o, idx) => ({ ...o, ist_korrekt: idx === i })),
    );
  };
  const addOption = () =>
    optionen.length < 6 &&
    setOptionen((prev) => [
      ...prev,
      { text: "", ist_korrekt: false, reihenfolge: prev.length },
    ]);
  const removeOption = (i: number) =>
    optionen.length > 2 &&
    setOptionen((prev) => prev.filter((_, idx) => idx !== i));

  const save = () => {
    if (!text.trim()) return toast.error("Frage-Text ist Pflicht.");
    if (optionen.some((o) => !o.text.trim()))
      return toast.error("Jede Option braucht Text.");
    if (optionen.filter((o) => o.ist_korrekt).length !== 1)
      return toast.error("Genau eine Option muss korrekt sein.");
    const payload: FrageInput = {
      kurs: kursId,
      text: text.trim(),
      erklaerung: erklaerung.trim(),
      reihenfolge: existing?.reihenfolge ?? newOrder ?? 0,
      optionen,
    };
    const cb = {
      onSuccess: () => {
        toast.success("Frage gespeichert.");
        onClose();
      },
      onError: () => toast.error("Speichern fehlgeschlagen."),
    };
    if (existing) update.mutate({ id: existing.id, payload }, cb);
    else create.mutate(payload, cb);
  };

  return (
    <div className="space-y-3 rounded border bg-card p-3 shadow-sm">
      <div>
        <Label htmlFor="frage-text">Frage *</Label>
        <textarea
          id="frage-text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={2}
          className="w-full rounded border border-input bg-background p-2 text-sm"
        />
      </div>

      <div>
        <Label>Antwort-Optionen ({optionen.length})</Label>
        <div className="mt-1 space-y-1">
          {optionen.map((o, i) => (
            <div key={i} className="flex items-center gap-2">
              <input
                type="radio"
                checked={o.ist_korrekt}
                onChange={() => setKorrekt(i)}
                aria-label={`Option ${i + 1} ist korrekt`}
              />
              <Input
                value={o.text}
                onChange={(e) => updateOption(i, { text: e.target.value })}
                placeholder={`Option ${i + 1}`}
              />
              {optionen.length > 2 && (
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={() => removeOption(i)}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              )}
            </div>
          ))}
        </div>
        {optionen.length < 6 && (
          <Button size="sm" variant="ghost" onClick={addOption} className="mt-1">
            <Plus className="mr-1 h-3 w-3" /> Option hinzufügen
          </Button>
        )}
      </div>

      <div>
        <Label htmlFor="frage-erklaerung">Erklärung (optional)</Label>
        <textarea
          id="frage-erklaerung"
          value={erklaerung}
          onChange={(e) => setErklaerung(e.target.value)}
          rows={2}
          className="w-full rounded border border-input bg-background p-2 text-sm"
          placeholder="Warum ist die korrekte Antwort richtig?"
        />
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={onClose}>
          Abbrechen
        </Button>
        <Button onClick={save} disabled={create.isPending || update.isPending}>
          {existing ? "Speichern" : "Anlegen"}
        </Button>
      </div>
    </div>
  );
}
