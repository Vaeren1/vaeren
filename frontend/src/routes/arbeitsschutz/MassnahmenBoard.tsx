/**
 * Maßnahmen-Board (Kanban-light) nach STOP-Hierarchie + Status.
 *
 * Banner-Warning: Wenn Gefährdungen nur O/P-Maßnahmen haben (keine
 * Substitution oder technische Maßnahme), zeigen wir einen Hinweis
 * im Sinne von ArbSchG §4 (S/T sind nach Möglichkeit zu bevorzugen).
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  listMassnahmen,
  type MassnahmeStatus,
  type Schutzmassnahme,
  type StopStufe,
} from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";

const STOP_LABEL: Record<StopStufe, string> = {
  S: "S — Substitution",
  T: "T — Technisch",
  O: "O — Organisatorisch",
  P: "P — PSA",
};

const STATUS_LABEL: Record<MassnahmeStatus, string> = {
  geplant: "Geplant",
  umgesetzt: "Umgesetzt",
  wirksam_geprueft: "Wirksamkeit geprüft",
  verworfen: "Verworfen",
};

const STATUS_COLOR: Record<MassnahmeStatus, string> = {
  geplant: "bg-amber-50 border-amber-200",
  umgesetzt: "bg-sky-50 border-sky-200",
  wirksam_geprueft: "bg-emerald-50 border-emerald-200",
  verworfen: "bg-slate-50 border-slate-200",
};

/**
 * Zählt, wie viele Gefährdungs-Positionen NUR durch O/P abgedeckt werden,
 * ohne mindestens eine S- oder T-Maßnahme. Maßnahmen mit Status
 * "verworfen" werden ignoriert.
 */
function countGefaehrdungenOhneST(massnahmen: Schutzmassnahme[]): number {
  const positionToStop = new Map<number, Set<StopStufe>>();
  for (const m of massnahmen) {
    if (m.status === "verworfen") continue;
    for (const gefId of m.gbu_gefaehrdungen) {
      const existing = positionToStop.get(gefId) ?? new Set<StopStufe>();
      existing.add(m.hierarchie_stufe);
      positionToStop.set(gefId, existing);
    }
  }
  let count = 0;
  for (const stops of positionToStop.values()) {
    if (!stops.has("S") && !stops.has("T")) count += 1;
  }
  return count;
}

export function MassnahmenBoardPage() {
  const { data, isLoading } = useQuery({ queryKey: ["as-massnahmen"], queryFn: listMassnahmen });

  if (isLoading) return <p>Lade…</p>;
  if (!data || data.results.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Schutzmaßnahmen</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Noch keine Maßnahmen angelegt. Maßnahmen entstehen aus
            Gefährdungs-Positionen in einer GBU.
          </p>
        </CardContent>
      </Card>
    );
  }

  const cols: MassnahmeStatus[] = ["geplant", "umgesetzt", "wirksam_geprueft"];

  // STOP-Hierarchie-Warnung: zähle Gefährdungs-Positionen, die nur
  // O- oder P-Maßnahmen haben (keine Substitution / technische Maßnahme).
  const gefaehrdungenOhneST = countGefaehrdungenOhneST(data.results);

  return (
    <div>
      <h2 className="text-lg font-semibold mb-3">Maßnahmen-Board (STOP)</h2>
      {gefaehrdungenOhneST > 0 && (
        <div
          role="alert"
          className="mb-4 border border-amber-300 bg-amber-50 text-amber-900 rounded p-3 text-sm"
        >
          <strong>Warnung:</strong> {gefaehrdungenOhneST}{" "}
          Gefährdungs-Position(en) haben nur organisatorische oder
          PSA-Maßnahmen — bitte STOP-Hierarchie prüfen. Nach ArbSchG §4
          sind Substitution (S) und technische Maßnahmen (T) bevorzugt
          zu prüfen, bevor O/P angesetzt werden.
        </div>
      )}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cols.map((status) => (
          <div key={status} className="space-y-2">
            <h3 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              {STATUS_LABEL[status]}
            </h3>
            {data.results
              .filter((m) => m.status === status)
              .map((m) => (
                <div
                  key={m.id}
                  className={`border rounded p-3 ${STATUS_COLOR[m.status]}`}
                >
                  <div className="flex justify-between items-start">
                    <p className="text-xs font-mono">{STOP_LABEL[m.hierarchie_stufe]}</p>
                    <p className="text-xs text-muted-foreground">{m.frist}</p>
                  </div>
                  <p className="text-sm font-medium mt-1">{m.titel}</p>
                  <p className="text-xs mt-1 text-muted-foreground">
                    {m.beschreibung.slice(0, 100)}
                  </p>
                </div>
              ))}
          </div>
        ))}
      </div>
    </div>
  );
}
