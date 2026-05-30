/**
 * Schritt 5 — Aktivieren: empfohlene Module als vorausgewählte Checkboxen.
 *
 * Aktiviert die gewählten Module (POST) und leitet danach ins Cockpit.
 */
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useState } from "react";
import { toast } from "sonner";
import { modulLabel } from "./constants";

interface Props {
  empfohlen: string[];
  onDone: (keys: string[]) => Promise<void> | void;
}

export function StepAktivieren({ empfohlen, onDone }: Props) {
  const [ausgewaehlt, setAusgewaehlt] = useState<string[]>(empfohlen);
  const [laedt, setLaedt] = useState(false);

  const toggle = (key: string) => {
    setAusgewaehlt((cur) =>
      cur.includes(key) ? cur.filter((k) => k !== key) : [...cur, key],
    );
  };

  const aktivieren = async () => {
    setLaedt(true);
    try {
      await onDone(ausgewaehlt);
    } catch {
      toast.error("Aktivierung fehlgeschlagen. Bitte erneut versuchen.");
      setLaedt(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Module aktivieren</CardTitle>
        <p className="text-sm text-muted-foreground">
          Wir haben die passenden Module vorausgewählt. Sie können die Auswahl
          jederzeit anpassen.
        </p>
      </CardHeader>
      <CardContent className="space-y-2">
        {empfohlen.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Keine Module zur Aktivierung empfohlen.
          </p>
        )}
        {empfohlen.map((key) => (
          <label
            key={key}
            className="flex items-center gap-3 rounded-md border p-3 text-sm"
          >
            <input
              type="checkbox"
              checked={ausgewaehlt.includes(key)}
              onChange={() => toggle(key)}
              className="h-4 w-4 rounded border-input"
            />
            <span className="font-medium">{modulLabel(key)}</span>
          </label>
        ))}
      </CardContent>
      <CardFooter className="justify-end">
        <Button onClick={aktivieren} disabled={laedt}>
          {laedt ? "Wird aktiviert …" : "Aktivieren & ins Cockpit"}
        </Button>
      </CardFooter>
    </Card>
  );
}
