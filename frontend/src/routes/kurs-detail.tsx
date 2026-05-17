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
import { ModulEditor } from "@/components/kurs/modul-editor";
import { QuizEditor } from "@/components/kurs/quiz-editor";
import { KATEGORIE_LABEL, useKurs } from "@/lib/api/schulungen";
import { Link, useParams } from "react-router-dom";

const MODUS_LABEL: Record<string, string> = {
  quiz: "Quiz",
  kenntnisnahme: "Kenntnisnahme",
  kenntnisnahme_lesezeit: "Kenntnisn. + Zeit",
};

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
              {data.ist_standardkatalog ? (
                <p className="mt-2 inline-block rounded bg-slate-100 px-2 py-0.5 text-xs">
                  Vaeren-Standard (read-only)
                </p>
              ) : (
                <p className="mt-2 inline-block rounded bg-emerald-50 px-2 py-0.5 text-xs text-emerald-900">
                  Eigener Kurs
                </p>
              )}
            </div>
            <div className="flex gap-2">
              {!data.ist_standardkatalog && (
                <Button asChild variant="outline" size="sm">
                  <Link to={`/kurse/${data.id}/bearbeiten`}>Bearbeiten</Link>
                </Button>
              )}
              <Button asChild variant="outline" size="sm">
                <Link to="/kurse">← Bibliothek</Link>
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4 text-sm md:grid-cols-4">
          <Metric label="Kategorie" value={KATEGORIE_LABEL[data.kategorie]} />
          <Metric label="Module" value={data.module.length} />
          <Metric label="Fragen" value={data.fragen.length} />
          <Metric label="Gültigkeit" value={`${data.gueltigkeit_monate} Mo.`} />
          <Metric
            label="Modus"
            value={MODUS_LABEL[data.quiz_modus] ?? data.quiz_modus}
          />
          {data.quiz_modus === "quiz" && (
            <Metric
              label="Bestehensschwelle"
              value={`${data.min_richtig_prozent} %`}
            />
          )}
          {data.quiz_modus === "kenntnisnahme_lesezeit" && (
            <Metric
              label="Min. Lesezeit"
              value={`${data.mindest_lesezeit_s} s/Modul`}
            />
          )}
          <Metric
            label="Zertifikat"
            value={data.zertifikat_aktiv ? "ja" : "nein"}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Module</CardTitle>
          <CardDescription>
            {data.ist_standardkatalog
              ? "Module in der Reihenfolge, wie Mitarbeitende sie sehen (read-only)."
              : "Module per Drag & Drop neu sortieren. Klick auf den Stift bearbeitet das Modul, Mülleimer löscht es."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ModulEditor
            kursId={data.id}
            module={data.module}
            readonly={data.ist_standardkatalog}
          />
        </CardContent>
      </Card>

      {data.quiz_modus === "quiz" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              Quiz-Pool ({data.fragen.length} Fragen)
            </CardTitle>
            <CardDescription>
              {data.ist_standardkatalog
                ? "Single-Choice. Korrekte Antwort grün markiert (interne Sicht — Mitarbeitende sehen die Markierung im Quiz NICHT)."
                : "Fragen manuell anlegen oder vom LLM aus den Modul-Texten vorschlagen lassen. Vorschläge müssen einzeln bestätigt werden (RDG-Layer-3)."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <QuizEditor
              kursId={data.id}
              fragen={data.fragen}
              readonly={data.ist_standardkatalog}
            />
          </CardContent>
        </Card>
      )}
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
