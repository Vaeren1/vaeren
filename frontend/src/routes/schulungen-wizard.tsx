import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useMitarbeiterList } from "@/lib/api/mitarbeiter";
import {
  useCreateWelle,
  useKursList,
  usePersonalisieren,
  useUpdateWelle,
  useVersenden,
  useZuweisen,
} from "@/lib/api/schulungen";

type Step = 1 | 2 | 3 | 4;

export function SchulungenWizardPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState<Step>(1);
  const [welleId, setWelleId] = useState<number | null>(null);
  const [kursId, setKursId] = useState<number | "">("");
  const [titel, setTitel] = useState("");
  const [deadline, setDeadline] = useState("");
  const [selectedMitarbeiter, setSelectedMitarbeiter] = useState<number[]>([]);
  const [einleitungsText, setEinleitungsText] = useState("");
  const [llmKontext, setLlmKontext] = useState("");

  const kurse = useKursList();
  const mitarbeiter = useMitarbeiterList();
  const createWelle = useCreateWelle();
  const updateWelle = useUpdateWelle(welleId ?? 0);
  const zuweisen = useZuweisen(welleId ?? 0);
  const personalisieren = usePersonalisieren(welleId ?? 0);
  const versenden = useVersenden(welleId ?? 0);

  // --- Step 1: Kurs + Titel + Deadline -------
  const onStep1Next = () => {
    if (!kursId || !titel || !deadline) {
      toast.error("Bitte alle Felder ausfüllen.");
      return;
    }
    createWelle.mutate(
      { kurs: Number(kursId), titel, deadline },
      {
        onSuccess: (welle) => {
          setWelleId(welle.id);
          setStep(2);
        },
        onError: () => toast.error("Welle konnte nicht angelegt werden."),
      },
    );
  };

  // --- Step 2: Mitarbeiter zuweisen ---------
  const onStep2Next = () => {
    if (selectedMitarbeiter.length === 0) {
      toast.error("Mindestens einen Mitarbeiter auswählen.");
      return;
    }
    zuweisen.mutate(selectedMitarbeiter, {
      onSuccess: (res) => {
        toast.success(`${res.zugewiesen} Mitarbeiter zugewiesen.`);
        setStep(3);
      },
      onError: () => toast.error("Zuweisen fehlgeschlagen."),
    });
  };

  // --- Step 3: Einleitungstext (LLM-Vorschlag) -------
  const onLlmRequest = () => {
    personalisieren.mutate(llmKontext, {
      onSuccess: (res) => {
        setEinleitungsText(res.vorschlag);
        toast.success(
          res.quelle === "llm" ? "LLM-Vorschlag geladen." : "Static-Fallback verwendet.",
        );
      },
      onError: () => toast.error("Vorschlag fehlgeschlagen."),
    });
  };

  const onStep3Next = () => {
    updateWelle.mutate(
      { einleitungs_text: einleitungsText },
      {
        onSuccess: () => setStep(4),
        onError: () => toast.error("Speichern fehlgeschlagen."),
      },
    );
  };

  // --- Step 4: Versenden ----------------------
  const onSend = () => {
    if (!window.confirm("E-Mails an alle Mitarbeiter versenden?")) return;
    versenden.mutate(undefined, {
      onSuccess: (res) => {
        toast.success(`Versendet an ${res.versendet_an} Mitarbeiter.`);
        navigate(welleId ? `/schulungen/${welleId}` : "/schulungen");
      },
      onError: () => toast.error("Versand fehlgeschlagen."),
    });
  };

  const toggleMitarbeiter = (id: number) => {
    setSelectedMitarbeiter((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          Schulungs-Welle anlegen — Schritt {step} / 4
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {step === 1 && (
          <>
            <div className="space-y-2">
              <Label htmlFor="kurs">Kurs auswählen</Label>
              <select
                id="kurs"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={kursId}
                onChange={(e) =>
                  setKursId(e.target.value ? Number(e.target.value) : "")
                }
              >
                <option value="">— bitte wählen —</option>
                {kurse.data?.results.map((k) => (
                  <option key={k.id} value={k.id}>
                    {k.titel} ({k.fragen_anzahl} Fragen)
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="titel">Titel der Welle</Label>
              <Input
                id="titel"
                value={titel}
                onChange={(e) => setTitel(e.target.value)}
                placeholder="z. B. Q2-Refresh DSGVO"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="deadline">Deadline</Label>
              <Input
                id="deadline"
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
            </div>
          </>
        )}

        {step === 2 && (
          <>
            <p className="text-sm text-muted-foreground">
              Wähle Mitarbeiter, die diese Schulung absolvieren sollen.
            </p>
            {mitarbeiter.isLoading && <p>Lade …</p>}
            <div className="max-h-96 overflow-auto rounded border">
              {mitarbeiter.data?.results.map((m) => (
                <label
                  key={m.id}
                  className="flex items-center gap-2 border-b px-3 py-2 last:border-b-0 hover:bg-muted/50"
                >
                  <input
                    type="checkbox"
                    checked={selectedMitarbeiter.includes(m.id)}
                    onChange={() => toggleMitarbeiter(m.id)}
                  />
                  <span>
                    {m.vorname} {m.nachname}{" "}
                    <span className="text-xs text-muted-foreground">
                      ({m.abteilung})
                    </span>
                  </span>
                </label>
              ))}
            </div>
            <p className="text-sm">
              {selectedMitarbeiter.length} Mitarbeiter ausgewählt
            </p>
          </>
        )}

        {step === 3 && (
          <>
            <div className="space-y-2">
              <Label htmlFor="kontext">Kontext für LLM-Vorschlag (optional)</Label>
              <Input
                id="kontext"
                value={llmKontext}
                onChange={(e) => setLlmKontext(e.target.value)}
                placeholder="z. B. Q2-Refresh nach Audit"
              />
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={onLlmRequest}
                disabled={personalisieren.isPending}
              >
                {personalisieren.isPending ? "Generiere …" : "Vorschlag holen"}
              </Button>
            </div>
            <div className="space-y-2">
              <Label htmlFor="einleitung">Einleitungstext</Label>
              <Textarea
                id="einleitung"
                rows={6}
                value={einleitungsText}
                onChange={(e) => setEinleitungsText(e.target.value)}
                placeholder="Optional. Wird in jede Einladungs-E-Mail eingefügt."
              />
              <p className="text-xs text-muted-foreground">
                Wenn leer: Standard-Begrüßung wird verwendet. LLM-Vorschläge sind
                immer Vorschlag — bitte vor Versand prüfen (RDG).
              </p>
            </div>
          </>
        )}

        {step === 4 && (
          <div className="space-y-3">
            <p>
              Bereit zum Versand. Es werden {selectedMitarbeiter.length} E-Mails
              gesendet (Console-Backend in Dev — Inhalte siehst du im
              Backend-Log).
            </p>
            <p className="text-sm text-muted-foreground">
              Nach Versand wechselt die Welle in den Status „Versendet" und
              kann nicht mehr bearbeitet werden.
            </p>
          </div>
        )}
      </CardContent>
      <CardFooter className="justify-between">
        <Button
          type="button"
          variant="outline"
          onClick={() => navigate("/schulungen")}
        >
          Abbrechen
        </Button>
        <div className="flex gap-2">
          {step > 1 && step < 4 && (
            <Button
              type="button"
              variant="outline"
              onClick={() => setStep((step - 1) as Step)}
            >
              Zurück
            </Button>
          )}
          {step === 1 && (
            <Button type="button" onClick={onStep1Next} disabled={createWelle.isPending}>
              {createWelle.isPending ? "Speichere …" : "Weiter"}
            </Button>
          )}
          {step === 2 && (
            <Button type="button" onClick={onStep2Next} disabled={zuweisen.isPending}>
              {zuweisen.isPending ? "Weise zu …" : "Weiter"}
            </Button>
          )}
          {step === 3 && (
            <Button type="button" onClick={onStep3Next} disabled={updateWelle.isPending}>
              {updateWelle.isPending ? "Speichere …" : "Weiter"}
            </Button>
          )}
          {step === 4 && (
            <Button type="button" onClick={onSend} disabled={versenden.isPending}>
              {versenden.isPending ? "Versende …" : "Jetzt versenden"}
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
