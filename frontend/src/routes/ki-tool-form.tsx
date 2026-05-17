/**
 * KI-Tool anlegen mit LLM-Risiko-Vorschlag (RDG-Layer-3 HITL).
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  type DatenkategorieSensibilitaet,
  type KIRisikoKlasse,
  type KIRisikoVorschlagResponse,
  type KIToolKategorie,
  createKITool,
  kiRisikoVorschlag,
} from "@/lib/api/ki_inventar";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const KAT_OPTIONS: { value: KIToolKategorie; label: string }[] = [
  { value: "llm_chatbot", label: "LLM / Chatbot" },
  { value: "bild_generierung", label: "Bild-Generierung" },
  { value: "ocr_text", label: "OCR / Text-Erkennung" },
  { value: "klassifizierung", label: "Klassifizierung / Predictive Analytics" },
  { value: "empfehlung", label: "Empfehlung / Recommender" },
  { value: "biometrie", label: "Biometrische Erkennung" },
  { value: "hr_recruiting", label: "HR / Recruiting (Hochrisiko)" },
  { value: "kredit_scoring", label: "Kredit-Scoring (Hochrisiko)" },
  { value: "produktion", label: "Produktions-/Maschinen-Steuerung" },
  { value: "sonstiges", label: "Sonstiges" },
];

export function KIToolFormPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [anbieter, setAnbieter] = useState("");
  const [kategorie, setKategorie] = useState<KIToolKategorie>("llm_chatbot");
  const [zweck, setZweck] = useState("");
  const [sensibilitaet, setSensibilitaet] = useState<DatenkategorieSensibilitaet>("keine_personendaten");
  const [risiko, setRisiko] = useState<KIRisikoKlasse>("unbekannt");
  const [submitting, setSubmitting] = useState(false);
  const [vorschlag, setVorschlag] = useState<KIRisikoVorschlagResponse | null>(null);
  const [vorschlagLoading, setVorschlagLoading] = useState(false);

  async function holeVorschlag() {
    if (zweck.length < 15) {
      toast.error("Bitte den Einsatzzweck konkret beschreiben (mindestens 15 Zeichen).");
      return;
    }
    setVorschlagLoading(true);
    try {
      const res = await kiRisikoVorschlag({
        name,
        anbieter,
        kategorie,
        zweck,
        datenkategorie_sensibilitaet: sensibilitaet,
      });
      setVorschlag(res);
    } catch {
      toast.error("Vorschlag konnte nicht abgerufen werden.");
    } finally {
      setVorschlagLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name || !anbieter || !zweck) {
      toast.error("Name, Anbieter und Zweck sind Pflicht.");
      return;
    }
    setSubmitting(true);
    try {
      const tool = await createKITool({
        name,
        anbieter,
        kategorie,
        zweck,
        datenkategorie_sensibilitaet: sensibilitaet,
        risiko: risiko === "unbekannt" ? undefined : risiko,
      });
      toast.success("KI-Tool erfasst.");
      navigate(`/ki-inventar/${tool.id}`);
    } catch {
      toast.error("Speichern fehlgeschlagen.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="max-w-3xl">
      <CardHeader>
        <CardTitle>KI-Tool erfassen</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Jedes im Unternehmen eingesetzte KI-System gehört ins Inventar (Art. 26 AI Act).
          Auch ChatGPT, Copilot, DeepL, Notion AI, etc.
        </p>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Tool-Name</Label>
              <Input id="name" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="anbieter">Anbieter</Label>
              <Input id="anbieter" value={anbieter} onChange={(e) => setAnbieter(e.target.value)} required />
            </div>
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="kategorie">Kategorie</Label>
              <select
                id="kategorie"
                value={kategorie}
                onChange={(e) => setKategorie(e.target.value as KIToolKategorie)}
                className="w-full px-3 py-2 border rounded"
              >
                {KAT_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="sensibilitaet">Personendaten-Sensibilität</Label>
              <select
                id="sensibilitaet"
                value={sensibilitaet}
                onChange={(e) => setSensibilitaet(e.target.value as DatenkategorieSensibilitaet)}
                className="w-full px-3 py-2 border rounded"
              >
                <option value="keine_personendaten">Keine Personendaten</option>
                <option value="gewoehnlich">Gewöhnliche Personendaten</option>
                <option value="besondere_kategorie">Besondere Kategorien (Art. 9 DSGVO)</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="zweck">Einsatzzweck</Label>
            <Textarea
              id="zweck"
              rows={3}
              value={zweck}
              onChange={(e) => setZweck(e.target.value)}
              placeholder="Wofür wird das Tool eingesetzt, von wem, in welchem Prozess?"
              required
            />
          </div>

          <div className="rounded border border-amber-300 bg-amber-50 p-3 space-y-2">
            <p className="text-sm font-semibold">AI-Act-Risiko-Vorschlag</p>
            <p className="text-xs">
              Der LLM-Vorschlag ist Orientierung — die finale Einstufung trifft Mensch +
              ggf. Rechtsabteilung. Hochrisiko-Bereiche aus Anhang III sind im AI Act
              abschließend gelistet.
            </p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={holeVorschlag}
              disabled={vorschlagLoading || !name || !anbieter || !zweck}
            >
              {vorschlagLoading ? "Vorschlag wird geholt …" : "LLM-Vorschlag holen"}
            </Button>
            {vorschlag && (
              <div className="mt-2 rounded bg-paper border border-line p-2 text-xs space-y-1">
                <p>
                  <strong>Vorschlag:</strong> {vorschlag.risiko_vorschlag}
                </p>
                <p>{vorschlag.begruendung}</p>
                <p className="italic text-amber-800">{vorschlag.rdg_disclaimer}</p>
              </div>
            )}
            <div>
              <Label htmlFor="risiko" className="text-xs">Finale Einstufung</Label>
              <select
                id="risiko"
                value={risiko}
                onChange={(e) => setRisiko(e.target.value as KIRisikoKlasse)}
                className="w-full px-3 py-2 border rounded text-sm"
              >
                <option value="unbekannt">— später entscheiden —</option>
                <option value="minimal">Minimal</option>
                <option value="begrenzt">Begrenzt (Transparenzpflicht)</option>
                <option value="hoch">Hoch (Anhang III)</option>
                <option value="unakzeptabel">Unakzeptabel (verboten)</option>
              </select>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={() => navigate("/ki-inventar")}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? "Speichern …" : "Tool erfassen"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
