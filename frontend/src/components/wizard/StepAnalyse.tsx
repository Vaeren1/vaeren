/**
 * Schritt 2 — Analyse: kurze Inszenierung "Wir analysieren Ihr Unternehmen".
 *
 * Die eigentliche Recherche lief bereits in Schritt 1 (StepStart) und das
 * Profil liegt vor. Dieser Schritt zeigt die erkannten Eckdaten und leitet
 * dann zur Bestätigung weiter — bewusst ein kurzer "Reveal"-Moment.
 */
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Profil } from "@/lib/api/onboarding";
import { merkmalLabel } from "./constants";

interface Props {
  profil: Profil;
  onNext: () => void;
}

export function StepAnalyse({ profil, onNext }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Das haben wir über {profil.firmenname} gefunden</CardTitle>
        <p className="text-sm text-muted-foreground">
          Bitte im nächsten Schritt prüfen und korrigieren. Nur eine erste
          Einschätzung — keine Rechtsberatung.
        </p>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <dl className="grid grid-cols-2 gap-x-4 gap-y-2">
          <dt className="text-muted-foreground">Branche</dt>
          <dd>{profil.branche || "—"}</dd>
          <dt className="text-muted-foreground">Mitarbeiter</dt>
          <dd>{profil.mitarbeiter_anzahl || "—"}</dd>
          <dt className="text-muted-foreground">Rechtsform</dt>
          <dd>{profil.rechtsform || "—"}</dd>
          <dt className="text-muted-foreground">NIS2-Sektor</dt>
          <dd>{profil.nis2_sektor || "—"}</dd>
        </dl>
        {profil.betriebsmerkmale.length > 0 && (
          <div>
            <p className="mb-1.5 text-muted-foreground">
              Erkannte Betriebsmerkmale
            </p>
            <div className="flex flex-wrap gap-1.5">
              {profil.betriebsmerkmale.map((k) => (
                <span
                  key={k}
                  className="rounded-full bg-secondary px-2.5 py-0.5 text-xs text-secondary-foreground"
                >
                  {merkmalLabel(k)}
                </span>
              ))}
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="justify-end">
        <Button onClick={onNext}>Angaben prüfen</Button>
      </CardFooter>
    </Card>
  );
}
