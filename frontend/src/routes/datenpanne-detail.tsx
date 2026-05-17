/**
 * Datenpannen-Detail. Zeigt Inhalt + Tasks + Maßnahmen + Aktionen.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  abschliessen,
  behoerdeMelden,
  createMassnahme,
  getDatenpanne,
} from "@/lib/api/datenpannen";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

export function DatenpanneDetailPage() {
  const { id } = useParams<{ id: string }>();
  const pid = id ? Number.parseInt(id, 10) : 0;
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["datenpanne", pid],
    queryFn: () => getDatenpanne(pid),
    enabled: !!pid,
  });

  const [aktenzeichen, setAktenzeichen] = useState("");
  const [massnahme, setMassnahme] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (isLoading) return <p>Lade …</p>;
  if (isError || !data) return <p className="text-destructive">Fehler beim Laden.</p>;

  async function handleMelden() {
    if (!aktenzeichen.trim()) {
      toast.error("Aktenzeichen darf nicht leer sein.");
      return;
    }
    setSubmitting(true);
    try {
      await behoerdeMelden(pid, aktenzeichen);
      toast.success("Behörden-Meldung dokumentiert.");
      qc.invalidateQueries({ queryKey: ["datenpanne", pid] });
    } catch {
      toast.error("Speichern fehlgeschlagen.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAbschluss() {
    setSubmitting(true);
    try {
      await abschliessen(pid);
      toast.success("Datenpanne abgeschlossen.");
      qc.invalidateQueries({ queryKey: ["datenpanne", pid] });
    } catch {
      toast.error("Speichern fehlgeschlagen.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleMassnahme() {
    if (!massnahme.trim()) return;
    setSubmitting(true);
    try {
      await createMassnahme({
        datenpanne: pid,
        typ: "sofort",
        beschreibung: massnahme,
      });
      setMassnahme("");
      qc.invalidateQueries({ queryKey: ["datenpanne", pid] });
    } catch {
      toast.error("Speichern fehlgeschlagen.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="space-y-4 max-w-4xl">
      <Card>
        <CardHeader>
          <CardTitle>{data.titel}</CardTitle>
          <p className="text-sm text-muted-foreground">
            Status: <strong>{data.status}</strong> · Risiko: <strong>{data.risiko || "noch nicht eingestuft"}</strong> · Frist: <strong>{Math.round(data.stunden_bis_meldefrist)} h</strong>
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm whitespace-pre-wrap">{data.beschreibung}</p>
          <div className="grid md:grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Entdeckt am</p>
              <p>{new Date(data.entdeckt_am).toLocaleString("de-DE")}</p>
            </div>
            <div>
              <p className="text-muted-foreground">72-h-Frist (Behörde)</p>
              <p>{new Date(data.frist_meldung_behoerde).toLocaleString("de-DE")}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Anzahl Betroffene (geschätzt)</p>
              <p>{data.anzahl_betroffene_geschaetzt ?? "unbekannt"}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Datenkategorien</p>
              <p>{data.datenkategorien.join(", ") || "—"}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Behörden-Meldung</CardTitle>
        </CardHeader>
        <CardContent>
          {data.behoerde_gemeldet_am ? (
            <div className="rounded bg-emerald-50 border border-emerald-200 p-3 text-sm">
              <p>
                Gemeldet am{" "}
                <strong>{new Date(data.behoerde_gemeldet_am).toLocaleString("de-DE")}</strong>
                {data.behoerde_aktenzeichen && ` · Aktenzeichen ${data.behoerde_aktenzeichen}`}.
              </p>
            </div>
          ) : (
            <div className="flex items-end gap-2">
              <div className="flex-1">
                <label className="text-sm text-muted-foreground">Aktenzeichen Aufsichtsbehörde</label>
                <Input
                  value={aktenzeichen}
                  onChange={(e) => setAktenzeichen(e.target.value)}
                  placeholder="z. B. BfDI-2026-0123"
                />
              </div>
              <Button onClick={handleMelden} disabled={submitting}>
                Als gemeldet markieren
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Maßnahmen ({data.massnahmen.length})</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {data.massnahmen.map((m) => (
            <div key={m.id} className="border rounded p-2 text-sm">
              <p className="text-xs text-muted-foreground">{m.typ}</p>
              <p>{m.beschreibung}</p>
            </div>
          ))}
          <div className="flex gap-2 items-end mt-3">
            <div className="flex-1">
              <label className="text-sm text-muted-foreground">Sofortmaßnahme erfassen</label>
              <Textarea
                rows={2}
                value={massnahme}
                onChange={(e) => setMassnahme(e.target.value)}
              />
            </div>
            <Button onClick={handleMassnahme} disabled={submitting}>
              + Hinzufügen
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tasks ({data.tasks.length})</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1.5">
          {data.tasks.map((t) => (
            <div key={t.id} className="text-sm flex justify-between border-b pb-1">
              <span>{t.titel}</span>
              <span className="text-muted-foreground">Frist: {t.frist} · {t.status}</span>
            </div>
          ))}
        </CardContent>
      </Card>

      {data.status !== "abgeschlossen" && (
        <div>
          <Button variant="outline" onClick={handleAbschluss} disabled={submitting}>
            Datenpanne abschließen
          </Button>
        </div>
      )}
    </div>
  );
}
