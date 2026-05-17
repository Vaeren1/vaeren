/**
 * Maßnahmen-Board (Kanban-light) nach STOP-Hierarchie + Status.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listMassnahmen, type MassnahmeStatus, type StopStufe } from "@/lib/api/arbeitsschutz";
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
  return (
    <div>
      <h2 className="text-lg font-semibold mb-3">Maßnahmen-Board (STOP)</h2>
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
