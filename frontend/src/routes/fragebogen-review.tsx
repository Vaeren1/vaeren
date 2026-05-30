/**
 * OEM-Fragebogen — seiten-basierter Review (Feature 4, G2).
 *
 * Funktionale Listen-Review (deckt xlsx-Demo + alle Tiers): die Fragen werden
 * nach `seite` gruppiert; pro Seite eine editierbare Antwort-Liste mit
 * Confidence + RDG-Status hervorgehoben, Quelle sichtbar. Text wird per PATCH
 * on-blur gespeichert (kein Klick pro Antwort). Pro Seite „Seite bestätigt",
 * Zurück-/Vorblättern, am Ende „Fragebogen final bestätigen" → final-attestieren
 * → Download (export).
 *
 * Bewusst als Listen-Variante angelegt: die volle visuelle Drag-Canvas (Box auf
 * gerendertem Seitenbild verschieben) hängt am Seiten-Bild-Rendering aus Phase H.
 * Diese Komponente ist so geschnitten, dass die Canvas-Variante pro Seite später
 * als alternatives Rendering ergänzt werden kann (`SeitenReview` austauschbar).
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import {
  type Antwort,
  type Frage,
  type FragebogenDetail,
  fragebogen,
} from "@/lib/api/fragebogen";
import { cn } from "@/lib/utils";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

// --- Hilfen --------------------------------------------------------------

/** Gruppiert die Fragen eines Fragebogens nach `seite` (aufsteigend). */
export function gruppiereNachSeite(fragen: Frage[]): Array<[number, Frage[]]> {
  const map = new Map<number, Frage[]>();
  for (const f of fragen) {
    const arr = map.get(f.seite) ?? [];
    arr.push(f);
    map.set(f.seite, arr);
  }
  return [...map.entries()].sort((a, b) => a[0] - b[0]);
}

function confidenceLabel(c: number): { text: string; cls: string } {
  if (c >= 0.75)
    return {
      text: `Hohe Sicherheit (${Math.round(c * 100)} %)`,
      cls: "text-emerald-700",
    };
  if (c >= 0.4)
    return {
      text: `Mittlere Sicherheit (${Math.round(c * 100)} %)`,
      cls: "text-amber-700",
    };
  return {
    text: `Niedrige Sicherheit (${Math.round(c * 100)} %) — bitte genau prüfen`,
    cls: "text-red-700 font-medium",
  };
}

// --- Einzelne Antwort-Karte ---------------------------------------------

function AntwortKarte({
  frage,
  antwort,
  fragebogenId,
}: {
  frage: Frage;
  antwort: Antwort;
  fragebogenId: number;
}) {
  const qc = useQueryClient();
  const [text, setText] = useState(antwort.finaler_text ?? "");
  const [dirty, setDirty] = useState(false);
  const conf = confidenceLabel(antwort.confidence);

  const patch = useMutation({
    mutationFn: () =>
      fragebogen.patchAntwort(fragebogenId, antwort.id, {
        bestaetigt_text: text,
      }),
    onSuccess: () => {
      setDirty(false);
      qc.invalidateQueries({ queryKey: ["fragebogen", fragebogenId] });
    },
  });

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="flex items-start justify-between gap-3">
        <p className="text-sm font-medium">
          {frage.nummer ? `${frage.nummer}. ` : ""}
          {frage.text}
        </p>
        <span className={cn("shrink-0 text-xs", conf.cls)}>{conf.text}</span>
      </div>

      {!antwort.rdg_ok && (
        <div className="rounded-md border border-red-300 bg-red-50 px-3 py-2 text-sm text-red-800">
          <strong>Verbotene Formulierung erkannt</strong> — der Vorschlag
          enthält eine unzulässige Rechtsaussage. Bitte umformulieren
          (Vorschlagssprache, keine Pflichtaussagen), bevor Sie die Seite
          bestätigen.
        </div>
      )}

      <Textarea
        value={text}
        rows={3}
        onChange={(e) => {
          setText(e.target.value);
          setDirty(true);
        }}
        onBlur={() => {
          if (dirty) patch.mutate();
        }}
        placeholder="Antwort-Text …"
      />

      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <span>
          {patch.isPending
            ? "Speichere …"
            : dirty
              ? "Ungespeicherte Änderung (wird beim Verlassen gespeichert)"
              : "Gespeichert"}
        </span>
        {antwort.quellen.length > 0 && (
          <span>
            Quelle:{" "}
            {antwort.quellen
              .map(
                (q) => `${q.quelle_typ}${q.referenz ? `:${q.referenz}` : ""}`,
              )
              .join(", ")}
          </span>
        )}
      </div>
    </div>
  );
}

// --- Eine Seite ----------------------------------------------------------

function SeitenReview({
  seite,
  fragen,
  fb,
  bestaetigt,
}: {
  seite: number;
  fragen: Frage[];
  fb: FragebogenDetail;
  bestaetigt: boolean;
}) {
  const qc = useQueryClient();
  const bestaetigen = useMutation({
    mutationFn: () => fragebogen.seiteBestaetigen(fb.id, seite),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["fragebogen", fb.id] }),
  });

  const rdgWarnungen = fragen.filter((f) => !f.antwort.rdg_ok).length;

  return (
    <div className="space-y-4">
      {fragen.map((f) => (
        <AntwortKarte
          key={f.id}
          frage={f}
          antwort={f.antwort}
          fragebogenId={fb.id}
        />
      ))}

      <div className="flex items-center justify-between border-t pt-4">
        <div className="text-sm">
          {bestaetigt ? (
            <span className="text-emerald-700 font-medium">
              ✓ Seite {seite} bestätigt
            </span>
          ) : rdgWarnungen > 0 ? (
            <span className="text-red-700">
              {rdgWarnungen} Antwort(en) mit verbotener Formulierung — erst
              umformulieren.
            </span>
          ) : (
            <span className="text-muted-foreground">
              Antworten geprüft? Dann Seite bestätigen.
            </span>
          )}
        </div>
        <Button
          type="button"
          disabled={bestaetigt || rdgWarnungen > 0 || bestaetigen.isPending}
          onClick={() => bestaetigen.mutate()}
        >
          {bestaetigen.isPending ? "Bestätige …" : "Seite bestätigt"}
        </Button>
      </div>
    </div>
  );
}

// --- Seite (Route) -------------------------------------------------------

export function FragebogenReviewPage() {
  const { id } = useParams<{ id: string }>();
  const fbId = Number(id);
  const navigate = useNavigate();
  const qc = useQueryClient();
  const [seitenIndex, setSeitenIndex] = useState(0);

  const detail = useQuery({
    queryKey: ["fragebogen", fbId],
    queryFn: () => fragebogen.detail(fbId),
    enabled: Number.isFinite(fbId),
  });

  const vorschlagen = useMutation({
    mutationFn: () => fragebogen.vorschlagen(fbId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["fragebogen", fbId] }),
  });

  const attestieren = useMutation({
    mutationFn: () => fragebogen.finalAttestieren(fbId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["fragebogen", fbId] }),
  });

  // Tier-2-Export läuft asynchron (202) — sobald der Job angestoßen ist,
  // pollen wir den Export-Status, bis die Datei bereit ist, und laden dann
  // automatisch herunter.
  const [tier2Wartet, setTier2Wartet] = useState(false);

  const exportieren = useMutation({
    mutationFn: () => fragebogen.exportieren(fbId),
    onSuccess: (res) => {
      qc.invalidateQueries({ queryKey: ["fragebogen", fbId] });
      // Union: Tier 1/3 → FragebogenDetail mit export_datei_url; Tier 2 → 202-Ack.
      if ("export_datei_url" in res && res.export_datei_url) {
        window.open(res.export_datei_url, "_blank", "noopener");
      } else if ("tier2_job_status" in res) {
        // Async-Pfad: auf Fertigstellung warten (Polling unten).
        setTier2Wartet(true);
      }
    },
  });

  // Polling des Export-Status während ein Tier-2-Job läuft.
  const exportStatus = useQuery({
    queryKey: ["fragebogen-export-status", fbId],
    queryFn: () => fragebogen.exportStatus(fbId),
    enabled: tier2Wartet,
    refetchInterval: (query) =>
      query.state.data?.export_bereit ? false : 2500,
  });

  // Sobald der Job fertig ist: Polling stoppen + Datei öffnen.
  useEffect(() => {
    if (!tier2Wartet) return;
    const s = exportStatus.data;
    if (s?.export_bereit && s.export_datei_url) {
      setTier2Wartet(false);
      qc.invalidateQueries({ queryKey: ["fragebogen", fbId] });
      window.open(s.export_datei_url, "_blank", "noopener");
    } else if (s?.tier2_job_status === "fehler") {
      setTier2Wartet(false);
    }
  }, [tier2Wartet, exportStatus.data, fbId, qc]);

  const fb = detail.data;
  const seiten = useMemo(() => (fb ? gruppiereNachSeite(fb.fragen) : []), [fb]);
  const bestaetigteSeiten = useMemo(
    () => new Set((fb?.bestaetigte_seiten as number[] | undefined) ?? []),
    [fb],
  );

  if (detail.isLoading) return <p>Lade …</p>;
  if (detail.isError || !fb)
    return <p className="text-destructive">Fehler beim Laden.</p>;

  // Noch keine Antwort-Entwürfe → Vorschlagen anbieten.
  const hatEntwuerfe = fb.fragen.some(
    (f) => f.antwort.entwurf_text || f.antwort.bestaetigt_text,
  );

  const aktuelleSeite = seiten[seitenIndex];
  const alleBestaetigt =
    seiten.length > 0 && seiten.every(([s]) => bestaetigteSeiten.has(s));

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>{fb.dateiname}</CardTitle>
            <p className="text-sm text-muted-foreground mt-1">
              Tier {fb.tier} · {fb.format} · {fb.quelle_oem || "OEM unbekannt"}{" "}
              · {seiten.length} Seite(n)
            </p>
          </div>
          <Button
            variant="outline"
            type="button"
            onClick={() => navigate("/fragebogen")}
          >
            Zur Übersicht
          </Button>
        </CardHeader>
        <CardContent>
          {!hatEntwuerfe ? (
            <div className="space-y-3">
              <p className="text-sm text-muted-foreground">
                Für diesen Fragebogen wurden noch keine Antworten vorgeschlagen.
              </p>
              {vorschlagen.isError && (
                <p className="text-sm text-destructive">
                  Vorschlag fehlgeschlagen.
                </p>
              )}
              <Button
                type="button"
                disabled={vorschlagen.isPending}
                onClick={() => vorschlagen.mutate()}
              >
                {vorschlagen.isPending
                  ? "Erzeuge Vorschläge …"
                  : "Antworten vorschlagen"}
              </Button>
            </div>
          ) : (
            <>
              {/* Seiten-Navigation */}
              <div className="mb-4 flex items-center justify-between">
                <Button
                  variant="outline"
                  type="button"
                  disabled={seitenIndex === 0}
                  onClick={() => setSeitenIndex((i) => Math.max(0, i - 1))}
                >
                  ‹ Vorige Seite
                </Button>
                <span className="text-sm font-medium">
                  Seite {aktuelleSeite ? aktuelleSeite[0] : "–"} (
                  {seitenIndex + 1}/{seiten.length})
                  {aktuelleSeite && bestaetigteSeiten.has(aktuelleSeite[0]) && (
                    <span className="ml-2 text-emerald-700">✓</span>
                  )}
                </span>
                <Button
                  variant="outline"
                  type="button"
                  disabled={seitenIndex >= seiten.length - 1}
                  onClick={() =>
                    setSeitenIndex((i) => Math.min(seiten.length - 1, i + 1))
                  }
                >
                  Nächste Seite ›
                </Button>
              </div>

              {aktuelleSeite && (
                <SeitenReview
                  seite={aktuelleSeite[0]}
                  fragen={aktuelleSeite[1]}
                  fb={fb}
                  bestaetigt={bestaetigteSeiten.has(aktuelleSeite[0])}
                />
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Finale Attestierung + Export */}
      {hatEntwuerfe && (
        <Card>
          <CardContent className="flex flex-col gap-3 pt-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="text-sm">
              {fb.final_attestiert ? (
                <span className="text-emerald-700 font-medium">
                  ✓ Fragebogen final attestiert
                </span>
              ) : alleBestaetigt ? (
                <span className="text-muted-foreground">
                  Alle Seiten bestätigt — Sie können final attestieren.
                </span>
              ) : (
                <span className="text-muted-foreground">
                  Erst alle Seiten bestätigen, dann final attestieren.
                </span>
              )}
            </div>
            <div className="flex gap-2">
              {!fb.final_attestiert ? (
                <Button
                  type="button"
                  disabled={!alleBestaetigt || attestieren.isPending}
                  onClick={() => attestieren.mutate()}
                >
                  {attestieren.isPending
                    ? "Attestiere …"
                    : "Fragebogen final bestätigen"}
                </Button>
              ) : (
                <div className="flex flex-col items-end gap-2">
                  <Button
                    type="button"
                    disabled={exportieren.isPending || tier2Wartet}
                    onClick={() => exportieren.mutate()}
                  >
                    {exportieren.isPending
                      ? "Erzeuge Export …"
                      : tier2Wartet
                        ? "Wird im Hintergrund erstellt …"
                        : fb.export_datei_url
                          ? "Ausgefüllten Fragebogen herunterladen"
                          : "Ausgefüllten Fragebogen exportieren"}
                  </Button>
                  {tier2Wartet && (
                    <span className="text-xs text-muted-foreground">
                      Der ausgefüllte Fragebogen (Overlay) wird im Hintergrund
                      erstellt — der Download startet automatisch, sobald er
                      fertig ist.
                    </span>
                  )}
                  {exportStatus.data?.tier2_job_status === "fehler" && (
                    <span className="text-xs text-destructive">
                      Der Export ist fehlgeschlagen. Bitte erneut versuchen.
                    </span>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
