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
  type PublicSchulungActive,
  isAbgeschlossen,
  usePublicAbschliessen,
  usePublicAntwort,
  usePublicSchulung,
  usePublicStart,
} from "@/lib/api/schulungen";
import { useEffect, useMemo, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import { toast } from "sonner";

type Phase = "loading" | "intro" | "lesen" | "quiz" | "ergebnis" | "fehler";

interface ErgebnisState {
  bestanden: boolean;
  richtig_prozent: number;
  zertifikat_token: string | null;
  zertifikat_aktiv: boolean;
}

function youtubeId(url: string): string | null {
  try {
    const u = new URL(url);
    if (u.hostname.includes("youtu.be")) return u.pathname.slice(1);
    if (u.hostname.includes("youtube.com")) {
      const v = u.searchParams.get("v");
      if (v) return v;
      const parts = u.pathname.split("/");
      const ei = parts.indexOf("embed");
      if (ei >= 0 && parts[ei + 1]) return parts[ei + 1];
    }
  } catch {
    return null;
  }
  return null;
}

function ModulAsset({ m }: { m: PublicSchulungActive["module"][number] }) {
  if (m.typ === "text") return <Markdown source={m.inhalt_md} />;
  if (m.typ === "video_youtube") {
    const id = youtubeId(m.youtube_url);
    if (!id) return <p className="text-destructive">YouTube-Link ungültig.</p>;
    return (
      <div className="aspect-video w-full">
        <iframe
          className="h-full w-full rounded"
          src={`https://www.youtube.com/embed/${id}`}
          title="YouTube"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
    );
  }
  const url = m.asset_url;
  if (!url) {
    return (
      <p className="text-sm text-muted-foreground">
        Material wird noch verarbeitet — bitte später neu laden.
      </p>
    );
  }
  if (m.typ === "pdf" || m.typ === "office")
    return (
      <iframe src={url} title="PDF" className="h-[600px] w-full rounded border" />
    );
  if (m.typ === "bild")
    return (
      <img
        src={url}
        alt="Modul-Bild"
        className="max-h-[600px] w-auto rounded border"
      />
    );
  if (m.typ === "video_upload")
    return (
      <video src={url} controls className="w-full rounded border" style={{ maxHeight: 600 }}>
        <track kind="captions" />
      </video>
    );
  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className="underline">
      Download
    </a>
  );
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
  const [besucht, setBesucht] = useState<Set<number>>(new Set());
  const [ergebnis, setErgebnis] = useState<ErgebnisState | null>(null);

  // Per-Modul-Lesezeit-Tracker (sekundenweise hochzählen wenn Tab sichtbar)
  const [modulSekunden, setModulSekunden] = useState<Record<number, number>>({});
  const visibleRef = useRef<boolean>(true);

  useEffect(() => {
    const onVis = () => {
      visibleRef.current = !document.hidden;
    };
    document.addEventListener("visibilitychange", onVis);
    return () => document.removeEventListener("visibilitychange", onVis);
  }, []);

  useEffect(() => {
    if (query.isLoading) return setPhase("loading");
    if (query.isError || !query.data) return setPhase("fehler");
    if (isAbgeschlossen(query.data)) {
      setPhase("ergebnis");
      setErgebnis({
        bestanden: query.data.bestanden ?? false,
        richtig_prozent: query.data.richtig_prozent ?? 0,
        zertifikat_token: query.data.zertifikat_token,
        zertifikat_aktiv: true,
      });
      return;
    }
    setPhase("intro");
  }, [query.data, query.isLoading, query.isError]);

  const data = query.data && !isAbgeschlossen(query.data) ? query.data : null;
  const fragen: PublicFrage[] = useMemo(() => data?.fragen ?? [], [data]);
  const quizModus = data?.quiz_modus ?? "quiz";
  const minLesezeit = data?.mindest_lesezeit_s ?? 0;

  // Ticker für Lesezeit
  useEffect(() => {
    if (phase !== "lesen" || quizModus !== "kenntnisnahme_lesezeit") return;
    const m = data?.module[moduleIdx];
    if (!m) return;
    const interval = setInterval(() => {
      if (visibleRef.current) {
        setModulSekunden((prev) => ({
          ...prev,
          [m.id]: (prev[m.id] ?? 0) + 1,
        }));
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [phase, quizModus, moduleIdx, data]);

  const markBesucht = (id: number) =>
    setBesucht((prev) => {
      if (prev.has(id)) return prev;
      const next = new Set(prev);
      next.add(id);
      return next;
    });

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
      { onError: () => toast.error("Antwort konnte nicht gespeichert werden.") },
    );
  };

  const allAnswered =
    fragen.length > 0 && fragen.every((f) => answers[f.id] !== undefined);

  const handleSubmit = () => {
    const payload =
      quizModus === "quiz"
        ? undefined
        : { besuchte_module: Array.from(besucht) };
    abschliessen.mutate(payload, {
      onSuccess: (res) => {
        setErgebnis({
          bestanden: res.bestanden,
          richtig_prozent: res.richtig_prozent,
          zertifikat_token: res.zertifikat_id ? (token ?? null) : null,
          zertifikat_aktiv: res.zertifikat_aktiv !== false,
        });
        setPhase("ergebnis");
      },
      onError: (e) => toast.error(`Abschließen fehlgeschlagen: ${e.message}`),
    });
  };

  if (phase === "loading") return <Centered>Lade Schulung …</Centered>;

  if (phase === "ergebnis" && ergebnis) {
    return <ErgebnisCard ergebnis={ergebnis} token={token ?? ""} />;
  }

  if (phase === "fehler" || !data) {
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

  if (phase === "intro") {
    const modusText = {
      quiz: `lesen, dann ${fragen.length} Fragen beantworten`,
      kenntnisnahme: 'lesen und am Ende mit „Verstanden" bestätigen',
      kenntnisnahme_lesezeit: `lesen (min. ${minLesezeit} s pro Modul) und am Ende mit „Verstanden" bestätigen`,
    }[quizModus];
    return (
      <Centered>
        <Card className="max-w-2xl">
          <CardHeader>
            <CardTitle>{data.kurs_titel}</CardTitle>
            <CardDescription>
              Frist: {data.deadline}
              {quizModus === "quiz" &&
                ` · Bestanden ab ${data.min_richtig_prozent} %`}
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
              Du wirst {data.module.length} Modul(e) {modusText}.
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
      // Keine Module → bei Quiz direkt Quiz, sonst Abschluss
      if (quizModus === "quiz") setPhase("quiz");
      return null;
    }
    const isLast = moduleIdx === data.module.length - 1;
    const sekVerstrichen = modulSekunden[m.id] ?? 0;
    const lesezeitOk =
      quizModus !== "kenntnisnahme_lesezeit" || sekVerstrichen >= minLesezeit;
    return (
      <Centered>
        <Card className="max-w-3xl">
          <CardHeader>
            <CardTitle>{m.titel}</CardTitle>
            <CardDescription>
              Modul {moduleIdx + 1} / {data.module.length}
              {quizModus === "kenntnisnahme_lesezeit" && (
                <>
                  {" · "}
                  Lesezeit: {sekVerstrichen}/{minLesezeit} s
                </>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ModulAsset m={m} />
          </CardContent>
          <CardFooter className="justify-between">
            <div className="text-xs text-muted-foreground">
              {!lesezeitOk
                ? '„Weiter" wird nach Ablauf der Mindest-Lesezeit aktiv.'
                : ""}
            </div>
            <div className="flex gap-2">
              {moduleIdx > 0 && (
                <Button
                  variant="outline"
                  onClick={() => setModuleIdx(moduleIdx - 1)}
                >
                  Zurück
                </Button>
              )}
              <Button
                disabled={!lesezeitOk}
                onClick={() => {
                  markBesucht(m.id);
                  if (isLast) {
                    if (quizModus === "quiz") {
                      setPhase("quiz");
                    } else {
                      handleSubmit();
                    }
                  } else {
                    setModuleIdx(moduleIdx + 1);
                  }
                }}
              >
                {isLast
                  ? quizModus === "quiz"
                    ? "Zum Quiz"
                    : "Verstanden — abschließen"
                  : "Weiter"}
              </Button>
            </div>
          </CardFooter>
        </Card>
      </Centered>
    );
  }

  // phase === "quiz" (nur erreichbar bei quizModus === "quiz")
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
  const showZertifikat =
    ergebnis.bestanden && ergebnis.zertifikat_token && ergebnis.zertifikat_aktiv;
  return (
    <Centered>
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle>
            {ergebnis.bestanden ? "Bestanden!" : "Nicht bestanden"}
          </CardTitle>
          <CardDescription>
            Ergebnis: {ergebnis.richtig_prozent} %
            {ergebnis.bestanden && !ergebnis.zertifikat_aktiv && (
              <>
                {" · "}
                <span className="text-muted-foreground">
                  Für diesen Kurs wird kein Zertifikat ausgestellt.
                </span>
              </>
            )}
          </CardDescription>
        </CardHeader>
        {showZertifikat && (
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
