/**
 * Schritt 3 — Bestätigen: vorausgefüllte Eckdaten editierbar, Betriebsmerkmal-
 * Chips (vorausgewählt), Merkmal-Dropdown (Voll-Katalog) + Freitext-Feld.
 *
 * Speichert das Profil (PATCH) und löst danach im Container die Radar-Berechnung
 * aus. Das PATCH setzt serverseitig `bestaetigt_at` (Wizard gilt als durchlaufen).
 */
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
import type { Profil } from "@/lib/api/onboarding";
import { useState } from "react";
import { ALLE_MERKMALE, merkmalLabel } from "./constants";

interface Props {
  profil: Profil;
  onNext: (patch: Partial<Profil>) => void;
  laedt?: boolean;
}

export function StepBestaetigen({ profil, onNext, laedt }: Props) {
  const [mitarbeiter, setMitarbeiter] = useState(
    String(profil.mitarbeiter_anzahl || ""),
  );
  const [rechtsform, setRechtsform] = useState(profil.rechtsform || "");
  const [setztKi, setSetztKi] = useState(profil.setzt_ki_ein);
  const [gesundheit, setGesundheit] = useState(
    profil.verarbeitet_gesundheits_sozialdaten,
  );
  const [merkmale, setMerkmale] = useState<string[]>(
    profil.betriebsmerkmale ?? [],
  );
  const [neuesMerkmal, setNeuesMerkmal] = useState("");
  const [freitext, setFreitext] = useState("");

  const toggleMerkmal = (key: string) => {
    setMerkmale((cur) =>
      cur.includes(key) ? cur.filter((k) => k !== key) : [...cur, key],
    );
  };

  const addMerkmal = () => {
    if (neuesMerkmal && !merkmale.includes(neuesMerkmal)) {
      setMerkmale((cur) => [...cur, neuesMerkmal]);
    }
    setNeuesMerkmal("");
  };

  const weiter = () => {
    const freitextListe = freitext
      .split("\n")
      .map((z) => z.trim())
      .filter(Boolean);
    onNext({
      mitarbeiter_anzahl: Number(mitarbeiter) || 0,
      rechtsform,
      setzt_ki_ein: setztKi,
      verarbeitet_gesundheits_sozialdaten: gesundheit,
      betriebsmerkmale: merkmale,
      betriebsmerkmale_freitext: freitextListe,
    });
  };

  const verfuegbar = ALLE_MERKMALE.filter((k) => !merkmale.includes(k));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Angaben prüfen & ergänzen</CardTitle>
        <p className="text-sm text-muted-foreground">
          Korrigieren Sie, was nicht stimmt. Diese Angaben bestimmen die
          erkannten Pflichten.
        </p>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-1.5">
            <Label htmlFor="mitarbeiter">Mitarbeiterzahl</Label>
            <Input
              id="mitarbeiter"
              type="number"
              min={0}
              value={mitarbeiter}
              onChange={(e) => setMitarbeiter(e.target.value)}
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="rechtsform">Rechtsform</Label>
            <Input
              id="rechtsform"
              value={rechtsform}
              onChange={(e) => setRechtsform(e.target.value)}
              placeholder="z. B. GmbH"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={setztKi}
              onChange={(e) => setSetztKi(e.target.checked)}
              className="h-4 w-4 rounded border-input"
            />
            Wir setzen KI-Systeme ein
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={gesundheit}
              onChange={(e) => setGesundheit(e.target.checked)}
              className="h-4 w-4 rounded border-input"
            />
            Wir verarbeiten Gesundheits-/Sozialdaten
          </label>
        </div>

        <div className="space-y-2">
          <Label>Betriebsmerkmale</Label>
          <div className="flex flex-wrap gap-1.5">
            {merkmale.length === 0 && (
              <span className="text-sm text-muted-foreground">
                Noch keine ausgewählt.
              </span>
            )}
            {merkmale.map((k) => (
              <button
                key={k}
                type="button"
                onClick={() => toggleMerkmal(k)}
                className="inline-flex items-center gap-1 rounded-full bg-primary px-2.5 py-0.5 text-xs font-medium text-primary-foreground"
              >
                {merkmalLabel(k)} <span aria-hidden>×</span>
              </button>
            ))}
          </div>
          <div className="flex gap-2">
            <select
              value={neuesMerkmal}
              onChange={(e) => setNeuesMerkmal(e.target.value)}
              className="h-9 flex-1 rounded-md border border-input bg-background px-2 text-sm"
            >
              <option value="">Merkmal hinzufügen …</option>
              {verfuegbar.map((k) => (
                <option key={k} value={k}>
                  {merkmalLabel(k)}
                </option>
              ))}
            </select>
            <Button
              type="button"
              variant="secondary"
              onClick={addMerkmal}
              disabled={!neuesMerkmal}
            >
              Hinzufügen
            </Button>
          </div>
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="freitext">
            Besonderheiten (Freitext, eine pro Zeile)
          </Label>
          <textarea
            id="freitext"
            value={freitext}
            onChange={(e) => setFreitext(e.target.value)}
            rows={3}
            placeholder="z. B. Eigene Galvanik-Anlage"
            className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
          />
          <p className="text-xs text-muted-foreground">
            Freitext-Angaben werden als KI-Einschätzung markiert und sind
            separat zu prüfen.
          </p>
        </div>
      </CardContent>
      <CardFooter className="justify-end">
        <Button onClick={weiter} disabled={laedt}>
          {laedt ? "Radar wird berechnet …" : "Compliance-Radar anzeigen"}
        </Button>
      </CardFooter>
    </Card>
  );
}
