/**
 * ASA-Kalender — 4 Quartals-Sitzungen pro Jahr.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listAsaSitzungen } from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";

export function AsaCalendarPage() {
  const { data, isLoading } = useQuery({ queryKey: ["as-asa-list"], queryFn: listAsaSitzungen });

  return (
    <Card>
      <CardHeader>
        <CardTitle>ASA-Sitzungen</CardTitle>
        <p className="text-sm text-muted-foreground">
          ASiG §11 — quartalsweise Pflicht ab 21 Beschäftigten.
        </p>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade…</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Noch keine ASA-Sitzungen geplant.
          </p>
        )}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-4">
          {data?.results.map((s) => (
            <div key={s.id} className="border rounded p-3">
              <p className="text-xs font-mono">{s.quartal}</p>
              <p className="text-sm font-semibold">{s.titel}</p>
              <p className="text-xs text-muted-foreground">
                {new Date(s.geplant_am).toLocaleString("de-DE")}
              </p>
              <p className="text-xs mt-2">Status: {s.status}</p>
              <p className="text-xs">{s.beschluesse.length} Beschlüsse</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
