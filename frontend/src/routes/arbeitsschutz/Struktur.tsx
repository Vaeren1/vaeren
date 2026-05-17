/**
 * Stammdaten-Verwaltung: Arbeitsbereiche + Tätigkeiten.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listArbeitsbereiche, listTaetigkeiten } from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";

export function StrukturPage() {
  const bereiche = useQuery({ queryKey: ["as-bereiche"], queryFn: listArbeitsbereiche });
  const taetigkeiten = useQuery({ queryKey: ["as-taetigkeiten"], queryFn: listTaetigkeiten });

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <Card>
        <CardHeader>
          <CardTitle>Arbeitsbereiche</CardTitle>
        </CardHeader>
        <CardContent>
          {bereiche.isLoading && <p>Lade…</p>}
          {bereiche.data && bereiche.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Noch keine Arbeitsbereiche angelegt.
            </p>
          )}
          <ul className="space-y-2">
            {bereiche.data?.results.map((b) => (
              <li key={b.id} className="border rounded p-3">
                <p className="font-medium">{b.name}</p>
                <p className="text-xs text-muted-foreground">
                  {b.typ} · {b.standort || "—"}
                </p>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tätigkeiten</CardTitle>
        </CardHeader>
        <CardContent>
          {taetigkeiten.isLoading && <p>Lade…</p>}
          {taetigkeiten.data && taetigkeiten.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Noch keine Tätigkeiten angelegt.
            </p>
          )}
          <ul className="space-y-2">
            {taetigkeiten.data?.results.map((t) => (
              <li key={t.id} className="border rounded p-3">
                <p className="font-medium">{t.name}</p>
                <p className="text-xs text-muted-foreground">
                  Bereich: {t.arbeitsbereich_name}
                </p>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}
