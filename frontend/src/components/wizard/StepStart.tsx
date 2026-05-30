/**
 * Schritt 1 — Start: Firmenname + Website (+ Demo-Schalter).
 *
 * Löst die Recherche aus. Im Demo-Modus liefert das Backend eine Fixture
 * (kein Live-LLM) — für die Bühnen-Präsentation der Default.
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
import { type Profil, onboarding } from "@/lib/api/onboarding";
import { useState } from "react";
import { toast } from "sonner";

interface Props {
  onDone: (profil: Profil) => void;
}

export function StepStart({ onDone }: Props) {
  const [firmenname, setFirmenname] = useState("");
  const [website, setWebsite] = useState("");
  const [demo, setDemo] = useState(true);
  const [laedt, setLaedt] = useState(false);

  const start = async () => {
    if (!firmenname.trim()) {
      toast.error("Bitte einen Firmennamen eingeben.");
      return;
    }
    setLaedt(true);
    try {
      const profil = await onboarding.recherche(
        firmenname.trim(),
        website.trim(),
        demo,
      );
      onDone(profil);
    } catch {
      toast.error("Recherche fehlgeschlagen. Bitte erneut versuchen.");
    } finally {
      setLaedt(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Willkommen bei Vaeren</CardTitle>
        <p className="text-sm text-muted-foreground">
          Sagen Sie uns, wer Sie sind — wir leiten daraus Ihre
          Compliance-Pflichten ab.
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-1.5">
          <Label htmlFor="firmenname">Firmenname</Label>
          <Input
            id="firmenname"
            value={firmenname}
            onChange={(e) => setFirmenname(e.target.value)}
            placeholder="z. B. Müller Präzisionstechnik GmbH"
            autoFocus
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="website">Website (optional)</Label>
          <Input
            id="website"
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="www.beispiel.de"
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-muted-foreground">
          <input
            type="checkbox"
            checked={demo}
            onChange={(e) => setDemo(e.target.checked)}
            className="h-4 w-4 rounded border-input"
          />
          Demo-Modus (vordefinierte Beispiel-Firma, ohne Live-Recherche)
        </label>
      </CardContent>
      <CardFooter className="justify-end">
        <Button onClick={start} disabled={laedt}>
          {laedt ? "Recherche läuft …" : "Analyse starten"}
        </Button>
      </CardFooter>
    </Card>
  );
}
