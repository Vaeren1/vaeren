/**
 * Kurs-Detail (intern). Zeigt Lerninhalt + Quiz mit MARKIERUNG der
 * korrekten Antwort. Für redaktionelle Vorprüfung bevor Konrad/CB den
 * Kurs an Mitarbeiter ausrollt.
 */
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Markdown } from "@/components/ui/markdown";
import { useKurs } from "@/lib/api/schulungen";
import { Check, X } from "lucide-react";
import { Link, useParams } from "react-router-dom";

export function KursDetailPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number.parseInt(id, 10) : undefined;
  const { data, isLoading, isError } = useKurs(numericId);

  if (isLoading) return <p>Lade …</p>;
  if (isError || !data) {
    return (
      <p className="text-destructive">
        Kurs nicht gefunden oder keine Berechtigung.
      </p>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>{data.titel}</CardTitle>
              <CardDescription className="mt-1">
                {data.beschreibung}
              </CardDescription>
            </div>
            <Button asChild variant="outline" size="sm">
              <Link to="/kurse">← Bibliothek</Link>
            </Button>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <Metric label="Module" value={data.module.length} />
          <Metric label="Fragen" value={data.fragen.length} />
          <Metric label="Gültigkeit" value={`${data.gueltigkeit_monate} Mo.`} />
          <Metric
            label="Bestehensschwelle"
            value={`${data.min_richtig_prozent} %`}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Lerninhalt</CardTitle>
          <CardDescription>
            Module in der Reihenfolge, wie Mitarbeitende sie sehen. Markdown-
            Quelltext (## Überschriften, **fett**, Listen) — wird im Quiz-
            Player als Klartext mit Zeilenumbrüchen angezeigt.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.module.map((m, idx) => (
            <div key={m.id} className="rounded border bg-muted/30 p-4">
              <div className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">
                Modul {idx + 1} / {data.module.length}
              </div>
              <h3 className="mb-2 text-sm font-semibold">{m.titel}</h3>
              <Markdown source={m.inhalt_md} />
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            Quiz ({data.fragen.length} Fragen)
          </CardTitle>
          <CardDescription>
            Single-Choice. Korrekte Antwort grün markiert (interne Sicht —
            Mitarbeitende sehen die Markierung NICHT). Erklärung erscheint bei
            den Mitarbeitenden nach Auswahl.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {data.fragen.map((f, idx) => (
            <div key={f.id} className="rounded border bg-muted/30 p-4">
              <div className="mb-1 text-xs uppercase tracking-wide text-muted-foreground">
                Frage {idx + 1}
              </div>
              <p className="mb-3 font-medium">{f.text}</p>
              <ul className="space-y-1">
                {f.optionen.map((o) => (
                  <li
                    key={o.id}
                    className={
                      o.ist_korrekt
                        ? "flex items-start gap-2 rounded bg-emerald-50 px-2 py-1 text-emerald-900"
                        : "flex items-start gap-2 rounded px-2 py-1 text-slate-700"
                    }
                  >
                    {o.ist_korrekt ? (
                      <Check
                        size={16}
                        className="mt-0.5 shrink-0 text-emerald-600"
                      />
                    ) : (
                      <X size={16} className="mt-0.5 shrink-0 text-slate-400" />
                    )}
                    <span>{o.text}</span>
                  </li>
                ))}
              </ul>
              {f.erklaerung && (
                <p className="mt-3 rounded border-l-2 border-emerald-400 bg-emerald-50/50 px-3 py-2 text-xs text-emerald-900">
                  <span className="font-medium">Erklärung:</span> {f.erklaerung}
                </p>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded border bg-background px-3 py-2">
      <div className="text-xs text-muted-foreground">{label}</div>
      <div className="text-base font-medium">{value}</div>
    </div>
  );
}
