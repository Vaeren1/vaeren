import { Button } from "@/components/ui/button";
import { Markdown } from "@/components/ui/markdown";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  type PublicFrage,
  isAbgeschlossen,
  usePublicAbschliessen,
  usePublicAntwort,
  usePublicSchulung,
  usePublicStart,
} from "@/lib/api/schulungen";
import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

type Phase = "loading" | "intro" | "lesen" | "quiz" | "ergebnis" | "fehler";

interface ErgebnisState {
  bestanden: boolean;
  richtig_prozent: number;
  zertifikat_token: string | null;
}

export function PublicSchulungPage() {
  const { token } = useParams<{ token: string }>();
  const query = usePublicSchulung(token);
  const start = usePublicStart(token ?? "");
  const antwort = usePublicAntwort(token ?? "");
  const abschliessen = usePublicAbschliessen(token ?? "");

  const [phase, setPhase] = useState<Phase>("loading");
  const [moduleIdx, setModuleIdx] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [ergebnis, setErgebnis] = useState<ErgebnisState | null>(null);

  useEffect(() => {
    if (query.isLoading) return setPhase("loading");
    if (query.isError || !query.data) return setPhase("fehler");
    if (isAbgeschlossen(query.data)) {
      setPhase("ergebnis");
      setErgebnis({
        bestanden: query.data.bestanden ?? false,
        richtig_prozent: query.data.richtig_prozent ?? 0,
        zertifikat_token: query.data.zertifikat_token,
      });
      return;
    }
    setPhase("intro");
  }, [query.data, query.isLoading, query.isError]);

  const data = query.data && !isAbgeschlossen(query.data) ? query.data : null;
  const fragen: PublicFrage[] = useMemo(() => data?.fragen ?? [], [data]);

  const handleStart = () => {
    start.mutate(undefined, {
      onSuccess: () => setPhase("lesen"),
      onError: () => toast.error("Start fehlgeschlagen."),
    });
  };

  const onAntwort = (frageId: number, optionId: number) => {
    setAnswers((prev) => ({ ...prev, [frageId]: optionId }));
    antwort.mutate(
      { frage_id: frageId, option_id: optionId },
      {
        onError: () => toast.error("Antwort konnte nicht gespeichert werden."),
      },
    );
  };

  const allAnswered =
    fragen.length > 0 && fragen.every((f) => answers[f.id] !== undefined);

  const handleSubmit = () => {
    abschliessen.mutate(undefined, {
      onSuccess: (res) => {
        setErgebnis({
          bestanden: res.bestanden,
          richtig_prozent: res.richtig_prozent,
          zertifikat_token: res.zertifikat_id ? (token ?? null) : null,
        });
        setPhase("ergebnis");
      },
      onError: () => toast.error("Abschließen fehlgeschlagen."),
    });
  };

  if (phase === "loading") return <Centered>Lade Schulung …</Centered>;

  if (phase === "fehler" || !data) {
    if (phase === "ergebnis" && ergebnis) {
      return <ErgebnisCard ergebnis={ergebnis} token={token ?? ""} />;
    }
    return (
      <Centered>
        <Card className="max-w-md">
          <CardHeader>
            <CardTitle>Link ungültig</CardTitle>
            <CardDescription>
              Dieser Schulungs-Link ist abgelaufen oder ungültig. Bitte wende
              dich an deinen QM-Verantwortlichen.
            </CardDescription>
          </CardHeader>
        </Card>
      </Centered>
    );
  }

  if (phase === "ergebnis" && ergebnis) {
    return <ErgebnisCard ergebnis={ergebnis} token={token ?? ""} />;
  }

  if (phase === "intro") {
    return (
      <Centered>
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>{data.kurs_titel}</CardTitle>
            <CardDescription>
              Frist: {data.deadline} · Bestanden ab {data.min_richtig_prozent} %
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {data.einleitungs_text && (
              <div className="whitespace-pre-wrap rounded border bg-muted/40 p-3 text-sm">
                {data.einleitungs_text}
              </div>
            )}
            {data.kurs_beschreibung && (
              <p className="text-sm">{data.kurs_beschreibung}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Du wirst {data.module.length} Lerninhalt-Block(s) lesen, dann{" "}
              {fragen.length} Fragen beantworten.
            </p>
          </CardContent>
          <CardFooter>
            <Button onClick={handleStart} disabled={start.isPending}>
              {start.isPending ? "Starte …" : "Schulung starten"}
            </Button>
          </CardFooter>
        </Card>
      </Centered>
    );
  }

  if (phase === "lesen") {
    const m = data.module[moduleIdx];
    if (!m) {
      // Keine Module → direkt Quiz
      setPhase("quiz");
      return null;
    }
    const isLast = moduleIdx === data.module.length - 1;
    return (
      <Centered>
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>{m.titel}</CardTitle>
            <CardDescription>
              Modul {moduleIdx + 1} / {data.module.length}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Markdown source={m.inhalt_md} />
          </CardContent>
          <CardFooter className="justify-end gap-2">
            {moduleIdx > 0 && (
              <Button
                variant="outline"
                onClick={() => setModuleIdx(moduleIdx - 1)}
              >
                Zurück
              </Button>
            )}
            <Button
              onClick={() => {
                if (isLast) setPhase("quiz");
                else setModuleIdx(moduleIdx + 1);
              }}
            >
              {isLast ? "Zum Quiz" : "Weiter"}
            </Button>
          </CardFooter>
        </Card>
      </Centered>
    );
  }

  // phase === "quiz"
  return (
    <Centered>
      <Card className="max-w-2xl">
        <CardHeader>
          <CardTitle>Quiz</CardTitle>
          <CardDescription>
            Beantworte alle {fragen.length} Fragen.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {fragen.map((f, idx) => (
            <fieldset key={f.id} className="space-y-2">
              <legend className="font-medium">
                {idx + 1}. {f.text}
              </legend>
              <div className="space-y-2">
                {f.optionen.map((opt) => (
                  <label
                    key={opt.id}
                    className="flex items-start gap-2 rounded border p-2 hover:bg-muted/50"
                  >
                    <input
                      type="radio"
                      name={`frage-${f.id}`}
                      checked={answers[f.id] === opt.id}
                      onChange={() => onAntwort(f.id, opt.id)}
                    />
                    <span>{opt.text}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          ))}
        </CardContent>
        <CardFooter>
          <Button
            onClick={handleSubmit}
            disabled={!allAnswered || abschliessen.isPending}
          >
            {abschliessen.isPending ? "Werte aus …" : "Quiz abschließen"}
          </Button>
        </CardFooter>
      </Card>
    </Centered>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen items-start justify-center bg-muted/40 p-4 pt-12">
      {children}
    </div>
  );
}

function ErgebnisCard({
  ergebnis,
  token,
}: {
  ergebnis: ErgebnisState;
  token: string;
}) {
  return (
    <Centered>
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>
            {ergebnis.bestanden ? "Bestanden!" : "Nicht bestanden"}
          </CardTitle>
          <CardDescription>
            Ergebnis: {ergebnis.richtig_prozent} % richtig
          </CardDescription>
        </CardHeader>
        {ergebnis.bestanden && ergebnis.zertifikat_token && (
          <CardFooter>
            <Button asChild>
              <a
                href={`/api/public/schulung/${ergebnis.zertifikat_token ?? token}/zertifikat/`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Zertifikat herunterladen
              </a>
            </Button>
          </CardFooter>
        )}
        {!ergebnis.bestanden && (
          <CardContent>
            <p className="text-sm text-muted-foreground">
              Bitte wende dich an deinen QM-Verantwortlichen für die nächsten
              Schritte.
            </p>
          </CardContent>
        )}
      </Card>
    </Centered>
  );
}
