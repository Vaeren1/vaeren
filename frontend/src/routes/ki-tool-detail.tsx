/**
 * KI-Tool-Detail.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  type KIToolCreatePayload,
  getKITool,
  updateKITool,
} from "@/lib/api/ki_inventar";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

export function KIToolDetailPage() {
  const { id } = useParams<{ id: string }>();
  const tid = id ? Number.parseInt(id, 10) : 0;
  const qc = useQueryClient();
  const { data, isLoading, isError } = useQuery({
    queryKey: ["ki-tool", tid],
    queryFn: () => getKITool(tid),
    enabled: !!tid,
  });
  const [submitting, setSubmitting] = useState(false);

  if (isLoading) return <p>Lade …</p>;
  if (isError || !data)
    return <p className="text-destructive">Fehler beim Laden.</p>;

  async function toggleField(
    field: "transparenz_information" | "menschliche_aufsicht",
  ) {
    if (!data) return;
    setSubmitting(true);
    try {
      const patch: Partial<KIToolCreatePayload> = { [field]: !data[field] };
      await updateKITool(tid, patch);
      qc.invalidateQueries({ queryKey: ["ki-tool", tid] });
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
          <CardTitle>{data.name}</CardTitle>
          <p className="text-sm text-muted-foreground">
            {data.anbieter} · Risiko: <strong>{data.risiko}</strong> · Status:{" "}
            {data.status}
          </p>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <p>{data.zweck}</p>
          <div className="grid md:grid-cols-2 gap-3">
            <div>
              <p className="text-muted-foreground">Funktions-Kategorie</p>
              <p>{data.kategorie}</p>
            </div>
            <div>
              <p className="text-muted-foreground">
                Personendaten-Sensibilität
              </p>
              <p>{data.datenkategorie_sensibilitaet}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Nutzer-Anzahl</p>
              <p>{data.nutzer_anzahl ?? "—"}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Eingeführt am</p>
              <p>{data.eingefuehrt_am ?? "—"}</p>
            </div>
          </div>
          {data.risiko_begruendung && (
            <div>
              <p className="text-muted-foreground">Begründung der Einstufung</p>
              <p>{data.risiko_begruendung}</p>
            </div>
          )}
          <div>
            <p className="text-muted-foreground">Verlinkungen</p>
            <ul className="text-sm space-y-1">
              {data.avv_link && (
                <li>
                  AVV/DPA:{" "}
                  <a href={data.avv_link} className="underline">
                    {data.avv_link}
                  </a>
                </li>
              )}
              {data.konformitaet_link && (
                <li>
                  Konformität:{" "}
                  <a href={data.konformitaet_link} className="underline">
                    {data.konformitaet_link}
                  </a>
                </li>
              )}
              {data.dpia_link && (
                <li>
                  DPIA:{" "}
                  <a href={data.dpia_link} className="underline">
                    {data.dpia_link}
                  </a>
                </li>
              )}
              {!data.avv_link && !data.konformitaet_link && !data.dpia_link && (
                <li className="text-muted-foreground">
                  Noch keine Verlinkungen hinterlegt.
                </li>
              )}
            </ul>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Deployer-Pflichten (Art. 26 AI Act)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">
                Personal über KI-Einsatz informiert?
              </p>
              <p className="text-xs text-muted-foreground">Art. 26 Abs. 7</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              disabled={submitting}
              onClick={() => toggleField("transparenz_information")}
            >
              {data.transparenz_information
                ? "✓ Ja"
                : "Nein — als erledigt markieren"}
            </Button>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Menschliche Aufsicht gewährleistet?</p>
              <p className="text-xs text-muted-foreground">
                Art. 14 — Override-Möglichkeit
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              disabled={submitting}
              onClick={() => toggleField("menschliche_aufsicht")}
            >
              {data.menschliche_aufsicht
                ? "✓ Ja"
                : "Nein — als erledigt markieren"}
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
            <div
              key={t.id}
              className="text-sm flex justify-between border-b pb-1"
            >
              <span>{t.titel}</span>
              <span className="text-muted-foreground">
                Frist: {t.frist} · {t.status}
              </span>
            </div>
          ))}
          {data.tasks.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Keine offenen Tasks.
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
