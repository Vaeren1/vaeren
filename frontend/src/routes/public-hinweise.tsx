/**
 * Public Hinweisgeber-Form (HinSchG §17). Kein Login, anonyme Submission.
 * Nach erfolgreichem Submit: Token + Status-URL anzeigen — Hinweisgeber muss
 * sich Token notieren, kein Reset möglich.
 */

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { type MeldungSubmitResponse, submitMeldung } from "@/lib/api/hinschg";
import { useState } from "react";
import { Link } from "react-router-dom";

export function PublicHinweisePage() {
  const [titel, setTitel] = useState("");
  const [beschreibung, setBeschreibung] = useState("");
  const [anonym, setAnonym] = useState(true);
  const [kontakt, setKontakt] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<MeldungSubmitResponse | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const res = await submitMeldung({
        titel,
        beschreibung,
        anonym,
        melder_kontakt: anonym ? "" : kontakt,
      });
      setResponse(res);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unbekannter Fehler bei der Übermittlung.",
      );
    } finally {
      setSubmitting(false);
    }
  }

  if (response) {
    return (
      <div className="container mx-auto max-w-2xl py-12">
        <Card>
          <CardHeader>
            <CardTitle>Meldung erfolgreich übermittelt</CardTitle>
            <CardDescription>
              Bitte notieren Sie Ihren Eingangs-Token. Mit ihm können Sie den
              Status Ihrer Meldung anonym abrufen — ein Reset ist NICHT möglich.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="rounded border-2 border-dashed bg-muted p-4">
              <p className="text-xs text-muted-foreground">
                Ihr Eingangs-Token
              </p>
              <p className="mt-1 break-all font-mono text-sm font-semibold">
                {response.eingangs_token}
              </p>
            </div>
            <div className="text-sm">
              <p>
                <strong>Status-Seite:</strong>{" "}
                <Link
                  to={`/hinweise/status/${response.eingangs_token}`}
                  className="underline"
                >
                  /hinweise/status/{response.eingangs_token.slice(0, 8)}…
                </Link>
              </p>
              <p className="mt-2 text-muted-foreground">
                Eine Rückmeldung erfolgt spätestens am{" "}
                <strong>{response.rueckmeldung_faellig_bis}</strong> (HinSchG
                §17 Abs. 4).
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => window.print()}
              className="w-full"
            >
              Token drucken
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-2xl py-12">
      <Card>
        <CardHeader>
          <CardTitle>Hinweis melden</CardTitle>
          <CardDescription>
            Vertraulicher Meldekanal nach Hinweisgeberschutzgesetz (HinSchG).
            Ihre Identität bleibt geschützt — wir empfangen Ihre Meldung
            verschlüsselt und beantworten sie binnen drei Monaten.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="titel">Kurztitel</Label>
              <Input
                id="titel"
                required
                maxLength={200}
                value={titel}
                onChange={(e) => setTitel(e.target.value)}
                placeholder="z. B. Verdacht auf unsachgemäße Entsorgung"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="beschreibung">Beschreibung</Label>
              <Textarea
                id="beschreibung"
                required
                rows={8}
                value={beschreibung}
                onChange={(e) => setBeschreibung(e.target.value)}
                placeholder="Was haben Sie beobachtet? Wann und wo? Wer ist beteiligt?"
              />
            </div>
            <div className="space-y-2 rounded border p-3">
              <Label className="flex items-center gap-2 text-sm font-normal">
                <input
                  type="checkbox"
                  checked={!anonym}
                  onChange={(e) => setAnonym(!e.target.checked)}
                  className="h-4 w-4"
                />
                Ich möchte nicht anonym bleiben (Kontakt für Rückfragen)
              </Label>
              {!anonym && (
                <Input
                  type="text"
                  required
                  maxLength={300}
                  value={kontakt}
                  onChange={(e) => setKontakt(e.target.value)}
                  placeholder="E-Mail-Adresse oder Telefonnummer"
                />
              )}
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? "Übermittle …" : "Meldung absenden"}
            </Button>
            <p className="text-xs text-muted-foreground">
              Mit Absenden bestätigen Sie, dass die Angaben nach Ihrem
              Wissensstand wahrheitsgemäß sind.
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
