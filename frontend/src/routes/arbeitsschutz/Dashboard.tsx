/**
 * Arbeitsschutz-Dashboard: KPIs + Quoten + nächste ASA.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  listAsaSitzungen,
  listBeauftragtenQuoten,
  listGbu,
  listMassnahmen,
  unfallStatistik,
} from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

export function ArbeitsschutzDashboardPage() {
  const gbu = useQuery({ queryKey: ["as-gbu"], queryFn: listGbu });
  const m = useQuery({ queryKey: ["as-massn"], queryFn: listMassnahmen });
  const unf = useQuery({
    queryKey: ["as-unfall-stat"],
    queryFn: unfallStatistik,
  });
  const quoten = useQuery({
    queryKey: ["as-quoten"],
    queryFn: listBeauftragtenQuoten,
  });
  const asa = useQuery({ queryKey: ["as-asa"], queryFn: listAsaSitzungen });

  const gbuQuote = gbu.data
    ? `${gbu.data.results.filter((g) => g.ist_aktuell).length} / ${gbu.data.count} aktuell`
    : "—";
  const offeneMassn =
    m.data?.results.filter((x) => x.status === "geplant").length ?? 0;
  const naechsteAsa = asa.data?.results.find((s) => s.status === "geplant");

  // Ohne diesen Hinweis sähe ein 500er-Fehler aus wie „alles in Ordnung" (0 offene
  // Maßnahmen, — Unfälle) — für ein Compliance-Dashboard ein gefährliches Falsch-Grün.
  const anyError =
    gbu.isError || m.isError || unf.isError || quoten.isError || asa.isError;

  return (
    <div className="space-y-4">
      {anyError && (
        <div className="rounded-md border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          Einige Kennzahlen konnten nicht geladen werden. Die angezeigten Werte
          sind möglicherweise unvollständig — bitte Seite neu laden.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">GBU-Quote</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{gbuQuote}</p>
            <Link to="/arbeitsschutz/gbu" className="text-xs underline">
              Übersicht öffnen
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Offene Maßnahmen</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{offeneMassn}</p>
            <Link to="/arbeitsschutz/massnahmen" className="text-xs underline">
              Maßnahmen-Board
            </Link>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Unfälle YTD</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{unf.data?.ytd_total ?? "—"}</p>
            <p className="text-xs text-muted-foreground">
              meldepfl. {unf.data?.ytd_meldepflichtig ?? "—"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Nächste ASA</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-base font-semibold">
              {naechsteAsa?.quartal ?? "—"}
            </p>
            <p className="text-xs text-muted-foreground">
              {naechsteAsa
                ? new Date(naechsteAsa.geplant_am).toLocaleDateString("de-DE")
                : "keine geplant"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Beauftragten-Quoten</CardTitle>
        </CardHeader>
        <CardContent>
          {quoten.isLoading && <p>Lade…</p>}
          {quoten.data && quoten.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Quoten-Check noch nicht ausgeführt.{" "}
              <Link to="/arbeitsschutz/beauftragte" className="underline">
                jetzt prüfen
              </Link>
            </p>
          )}
          {quoten.data && quoten.data.results.length > 0 && (
            <div className="space-y-2">
              {quoten.data.results.map((q) => (
                <div key={q.id} className="flex items-center justify-between">
                  <span className="text-sm">{q.typ}</span>
                  <span
                    className={
                      q.erfuellt
                        ? "text-emerald-700"
                        : "text-rose-700 font-semibold"
                    }
                  >
                    {q.ist} / {q.soll} ({q.quote_prozent}%)
                  </span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <div className="text-sm text-muted-foreground">
        <p>
          Arbeitsschutz-Modul nach ArbSchG + DGUV. Vorschläge des Systems sind
          immer HITL — verbindlich entscheidet die Fachkraft für
          Arbeitssicherheit.
        </p>
      </div>
    </div>
  );
}
