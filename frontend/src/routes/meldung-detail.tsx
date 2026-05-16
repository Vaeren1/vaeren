/**
 * Meldung-Detail-Seite. Zeigt entschlüsselten Inhalt + Pflicht-Tasks +
 * Bearbeitungsschritte. Bestätigen / Abschließen / Bearbeitungsschritt anlegen.
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
import {
  type MeldungStatusValue,
  useAbschliessen,
  useAddBearbeitungsschritt,
  useBestaetigen,
  useMeldung,
  usePatchMeldung,
} from "@/lib/api/hinschg";
import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

const STATUS_OPTIONS: Array<[MeldungStatusValue, string]> = [
  ["eingegangen", "Eingegangen"],
  ["bestaetigt", "Eingangsbestätigung versandt"],
  ["in_pruefung", "In Prüfung"],
  ["massnahme", "Maßnahme eingeleitet"],
  ["abgeschlossen", "Abgeschlossen"],
  ["abgewiesen", "Abgewiesen"],
];

const SCHWEREGRADE = ["niedrig", "mittel", "hoch", "kritisch"];

export function MeldungDetailPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number.parseInt(id, 10) : undefined;
  const { data, isLoading, isError } = useMeldung(numericId);
  const patch = usePatchMeldung(numericId ?? 0);
  const bestaetigen = useBestaetigen(numericId ?? 0);
  const abschliessen = useAbschliessen(numericId ?? 0);
  const addSchritt = useAddBearbeitungsschritt(numericId ?? 0);

  const [aktion, setAktion] = useState("klassifizierung");
  const [notiz, setNotiz] = useState("");

  // Lokaler State für die Klassifizierungs-Felder. Hintergrund: der vorherige
  // Code hatte ein controlled `<Input value={data.kategorie}>` mit einem
  // No-Op-onChange — React rendert dann Tastatureingaben nicht. Lokaler
  // State plus useEffect-Hydrierung löst das.
  const [kategorie, setKategorie] = useState("");
  const [schweregrad, setSchweregrad] = useState("");
  const [statusValue, setStatusValue] =
    useState<MeldungStatusValue>("eingegangen");

  useEffect(() => {
    if (data) {
      setKategorie(data.kategorie ?? "");
      setSchweregrad(data.schweregrad ?? "");
      setStatusValue(data.status);
    }
  }, [data]);

  if (isLoading) return <p>Lade …</p>;
  if (isError || !data) {
    return (
      <p className="text-destructive">
        Keine Berechtigung oder Meldung nicht gefunden.
      </p>
    );
  }

  const isAbgeschlossen = data.status === "abgeschlossen";

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="break-all">
            {data.titel_verschluesselt}
          </CardTitle>
          <CardDescription>
            Token: <span className="font-mono">{data.eingangs_token}</span> ·
            Status: {data.status_display} · Eingang:{" "}
            {new Date(data.eingegangen_am).toLocaleString("de-DE")} ·{" "}
            {data.anonym ? "anonym" : "mit Kontakt"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <h3 className="mb-1 text-sm font-medium">Beschreibung</h3>
            <pre className="whitespace-pre-wrap rounded border bg-muted/40 p-3 text-sm">
              {data.beschreibung_verschluesselt}
            </pre>
          </div>
          {!data.anonym && data.melder_kontakt_verschluesselt && (
            <div>
              <h3 className="mb-1 text-sm font-medium">Kontakt Hinweisgeber</h3>
              <p className="rounded border bg-muted/40 p-3 text-sm">
                {data.melder_kontakt_verschluesselt}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Klassifizierung</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid gap-3 md:grid-cols-3">
            <div className="space-y-1">
              <Label htmlFor="kategorie">Kategorie</Label>
              <Input
                id="kategorie"
                value={kategorie}
                disabled={isAbgeschlossen}
                onChange={(e) => setKategorie(e.target.value)}
                onBlur={(e) => {
                  if (e.target.value !== (data.kategorie ?? "")) {
                    patch.mutate({ kategorie: e.target.value });
                  }
                }}
                placeholder="z. B. Korruption, Diskriminierung, Compliance"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="schweregrad">Schweregrad</Label>
              <select
                id="schweregrad"
                disabled={isAbgeschlossen}
                value={schweregrad}
                onChange={(e) => {
                  setSchweregrad(e.target.value);
                  patch.mutate({ schweregrad: e.target.value });
                }}
                className="w-full rounded border bg-background px-2 py-2 text-sm"
              >
                <option value="">— bitte wählen —</option>
                {SCHWEREGRADE.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1">
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                disabled={isAbgeschlossen}
                value={statusValue}
                onChange={(e) => {
                  const v = e.target.value as MeldungStatusValue;
                  setStatusValue(v);
                  patch.mutate({ status: v });
                }}
                className="w-full rounded border bg-background px-2 py-2 text-sm"
              >
                {STATUS_OPTIONS.map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex gap-2 pt-2">
            <Button
              variant="outline"
              disabled={
                bestaetigen.isPending ||
                data.bestaetigung_versandt_am !== null ||
                isAbgeschlossen
              }
              onClick={() => bestaetigen.mutate()}
            >
              Eingangsbestätigung versendet markieren
            </Button>
            <Button
              variant="destructive"
              disabled={abschliessen.isPending || isAbgeschlossen}
              onClick={() => abschliessen.mutate()}
            >
              Meldung abschließen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>HinSchG-Pflicht-Tasks</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm">
            {data.tasks.map((t) => (
              <li key={t.id} className="flex justify-between border-b pb-1">
                <span>{t.pflicht_typ_display}</span>
                <span>
                  Frist: {t.frist} · Status: {t.status}
                </span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Bearbeitungsschritte</CardTitle>
          <CardDescription>
            Append-only Audit. Notizen sind verschlüsselt gespeichert.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {data.bearbeitungsschritte.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Bisher keine Schritte.
            </p>
          ) : (
            <ul className="space-y-2 text-sm">
              {data.bearbeitungsschritte.map((s) => (
                <li key={s.id} className="rounded border bg-muted/40 p-3">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>
                      {s.bearbeiter_email ?? "Hinweisgeber:in (anonym)"}
                    </span>
                    <span>{new Date(s.timestamp).toLocaleString("de-DE")}</span>
                  </div>
                  <div className="mt-1 font-medium">{s.aktion}</div>
                  <pre className="mt-1 whitespace-pre-wrap text-sm">
                    {s.notiz_verschluesselt}
                  </pre>
                </li>
              ))}
            </ul>
          )}
          {!isAbgeschlossen && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                addSchritt.mutate(
                  { aktion, notiz_verschluesselt: notiz },
                  { onSuccess: () => setNotiz("") },
                );
              }}
              className="space-y-2 border-t pt-3"
            >
              <div className="grid gap-2 md:grid-cols-2">
                <div className="space-y-1">
                  <Label htmlFor="aktion">Aktion</Label>
                  <Input
                    id="aktion"
                    required
                    value={aktion}
                    onChange={(e) => setAktion(e.target.value)}
                    placeholder="z. B. ruecksprache_personal"
                  />
                </div>
              </div>
              <div className="space-y-1">
                <Label htmlFor="notiz">Notiz (verschlüsselt gespeichert)</Label>
                <Textarea
                  id="notiz"
                  required
                  rows={4}
                  value={notiz}
                  onChange={(e) => setNotiz(e.target.value)}
                />
              </div>
              <Button type="submit" disabled={addSchritt.isPending}>
                Schritt anlegen
              </Button>
            </form>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
