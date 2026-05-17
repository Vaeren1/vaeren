/**
 * Datenpanne anlegen (DSGVO Art. 33).
 *
 * Felder:
 * - Titel + Art (Klassifizierung)
 * - Beschreibung (verschlüsselt at-rest)
 * - Entdeckt-am (startet 72-h-Frist)
 * - Anzahl Betroffene + Datenkategorien
 *
 * Optional: LLM-Risiko-Vorschlag (RDG-Layer-3 HITL — KEIN Auto-Apply).
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  createDatenpanne,
  type DatenpanneCreatePayload,
  type PannenArt,
  type RisikoStufe,
  risikoVorschlag,
  type RisikoVorschlagResponse,
} from "@/lib/api/datenpannen";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";

const ART_OPTIONS: { value: PannenArt; label: string }[] = [
  { value: "verlust_geraet", label: "Verlust/Diebstahl Endgerät" },
  { value: "phishing", label: "Phishing/Social-Engineering" },
  { value: "ransomware", label: "Ransomware/Malware" },
  { value: "fehlversand", label: "Fehlversand (Mail/Brief)" },
  { value: "unberechtigter_zugriff", label: "Unberechtigter Zugriff" },
  { value: "konfigurationsfehler", label: "Konfiguration/Berechtigung" },
  { value: "systemausfall", label: "Systemausfall mit Daten-Auswirkung" },
  { value: "insider", label: "Insider-Vorfall" },
  { value: "sonstiges", label: "Sonstiges" },
];

const DATENKATEGORIEN_OPTIONS = [
  "kontaktdaten",
  "stammdaten",
  "vertragsdaten",
  "kontodaten",
  "kommunikationsdaten",
  "gesundheitsdaten",
  "biometrische_daten",
  "sozialversicherung",
  "kinderdaten",
];

export function DatenpanneFormPage() {
  const navigate = useNavigate();
  const [titel, setTitel] = useState("");
  const [art, setArt] = useState<PannenArt>("phishing");
  const [beschreibung, setBeschreibung] = useState("");
  const [entdecktAm, setEntdecktAm] = useState(() => new Date().toISOString().slice(0, 16));
  const [anzahl, setAnzahl] = useState<string>("");
  const [datenkategorien, setDatenkategorien] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);

  const [vorschlag, setVorschlag] = useState<RisikoVorschlagResponse | null>(null);
  const [vorschlagLoading, setVorschlagLoading] = useState(false);
  const [risiko, setRisiko] = useState<RisikoStufe>("");

  function toggleKategorie(k: string) {
    setDatenkategorien((cur) =>
      cur.includes(k) ? cur.filter((c) => c !== k) : [...cur, k],
    );
  }

  async function holeVorschlag() {
    if (beschreibung.length < 20) {
      toast.error("Bitte mindestens 20 Zeichen Beschreibung — sonst hat der Vorschlag keine Substanz.");
      return;
    }
    setVorschlagLoading(true);
    try {
      const res = await risikoVorschlag({
        art,
        beschreibung,
        anzahl_betroffene: anzahl ? Number.parseInt(anzahl, 10) : undefined,
        datenkategorien,
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
    if (titel.length < 3 || beschreibung.length < 5) {
      toast.error("Titel und Beschreibung sind Pflicht.");
      return;
    }
    setSubmitting(true);
    try {
      const payload: DatenpanneCreatePayload = {
        titel,
        art,
        beschreibung,
        entdeckt_am: new Date(entdecktAm).toISOString(),
        anzahl_betroffene_geschaetzt: anzahl ? Number.parseInt(anzahl, 10) : undefined,
        datenkategorien,
      };
      const created = await createDatenpanne(payload);
      // Falls Mensch finales Risiko gewählt hat: PATCH hinterher
      if (risiko) {
        // import dynamisch um Compile-Zeit zu sparen
        const { updateDatenpanne } = await import("@/lib/api/datenpannen");
        await updateDatenpanne(created.id, { risiko });
      }
      toast.success("Datenpanne erfasst — 72-h-Frist läuft.");
      navigate(`/datenpannen/${created.id}`);
    } catch {
      toast.error("Speichern fehlgeschlagen.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="max-w-3xl">
      <CardHeader>
        <CardTitle>Neue Datenpanne erfassen</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          DSGVO Art. 33: Meldepflichtige Datenpannen müssen <strong>binnen 72 Stunden</strong> nach
          Bekanntwerden an die Aufsichtsbehörde gemeldet werden. Erfassen Sie auch nicht-meldepflichtige
          Vorfälle — die Dokumentationspflicht (Art. 33 Abs. 5) gilt immer.
        </p>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="titel">Kurztitel</Label>
            <Input id="titel" value={titel} onChange={(e) => setTitel(e.target.value)} required />
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="art">Art</Label>
              <select
                id="art"
                value={art}
                onChange={(e) => setArt(e.target.value as PannenArt)}
                className="w-full px-3 py-2 border rounded"
              >
                {ART_OPTIONS.map((o) => (
                  <option key={o.value} value={o.value}>
                    {o.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="entdeckt_am">Entdeckt am</Label>
              <Input
                id="entdeckt_am"
                type="datetime-local"
                value={entdecktAm}
                onChange={(e) => setEntdecktAm(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="beschreibung">Beschreibung (verschlüsselt gespeichert)</Label>
            <Textarea
              id="beschreibung"
              rows={5}
              value={beschreibung}
              onChange={(e) => setBeschreibung(e.target.value)}
              placeholder="Was ist passiert, wo, wann, wer war beteiligt?"
              required
            />
          </div>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="anzahl">Geschätzte Anzahl Betroffene</Label>
              <Input
                id="anzahl"
                type="number"
                min="0"
                value={anzahl}
                onChange={(e) => setAnzahl(e.target.value)}
                placeholder="unbekannt"
              />
            </div>
            <div className="space-y-2">
              <Label>Datenkategorien</Label>
              <div className="flex flex-wrap gap-1.5">
                {DATENKATEGORIEN_OPTIONS.map((k) => (
                  <button
                    type="button"
                    key={k}
                    onClick={() => toggleKategorie(k)}
                    className={`text-xs px-2 py-1 rounded border ${
                      datenkategorien.includes(k)
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-background"
                    }`}
                  >
                    {k}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="rounded border border-amber-300 bg-amber-50 p-3 space-y-2">
            <p className="text-sm font-semibold">Risiko-Bewertung (RDG-Layer-3)</p>
            <p className="text-xs">
              LLM-Vorschlag ist optional und nur Orientierung. Die finale Einstufung trifft
              <strong> der/die Compliance-Verantwortliche</strong>.
            </p>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={holeVorschlag}
              disabled={vorschlagLoading}
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
            <div className="space-y-1">
              <Label htmlFor="risiko" className="text-xs">Finale Einstufung (Mensch entscheidet)</Label>
              <select
                id="risiko"
                value={risiko}
                onChange={(e) => setRisiko(e.target.value as RisikoStufe)}
                className="w-full px-3 py-2 border rounded text-sm"
              >
                <option value="">— später entscheiden —</option>
                <option value="kein_risiko">Kein Risiko</option>
                <option value="gering">Geringes Risiko (meldepflichtig)</option>
                <option value="hoch">Hohes Risiko (+ Betroffene benachrichtigen)</option>
              </select>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={() => navigate("/datenpannen")}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={submitting}>
            {submitting ? "Speichern …" : "Datenpanne erfassen + 72-h-Frist starten"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
