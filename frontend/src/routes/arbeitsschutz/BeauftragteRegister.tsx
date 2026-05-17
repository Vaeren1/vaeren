/**
 * Beauftragten-Register mit Quoten-Indikator.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  listBeauftragte,
  listBeauftragtenQuoten,
  refreshBeauftragtenQuoten,
} from "@/lib/api/arbeitsschutz";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

export function BeauftragteRegisterPage() {
  const qc = useQueryClient();
  const list = useQuery({ queryKey: ["as-beauf"], queryFn: listBeauftragte });
  const quoten = useQuery({ queryKey: ["as-quoten"], queryFn: listBeauftragtenQuoten });
  const refresh = useMutation({
    mutationFn: refreshBeauftragtenQuoten,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["as-quoten"] }),
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Quoten-Status</CardTitle>
            <p className="text-xs text-muted-foreground">
              SiBe ab 21 MA, Ersthelfer 1/10 MA (DGUV V1).
            </p>
          </div>
          <Button onClick={() => refresh.mutate()} disabled={refresh.isPending}>
            Quoten neu berechnen
          </Button>
        </CardHeader>
        <CardContent>
          {quoten.data && quoten.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Noch keine Quoten berechnet — Button oben rechts.
            </p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {quoten.data?.results.map((q) => (
              <div
                key={q.id}
                className={`border rounded p-3 ${
                  q.erfuellt ? "border-emerald-200 bg-emerald-50" : "border-rose-200 bg-rose-50"
                }`}
              >
                <p className="text-sm font-medium">{q.typ}</p>
                <p className="text-2xl font-bold mt-1">
                  {q.ist} / {q.soll}
                </p>
                <p className="text-xs text-muted-foreground">{q.quote_prozent}%</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Beauftragte</CardTitle>
        </CardHeader>
        <CardContent>
          {list.data && list.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Noch keine Beauftragten bestellt.
            </p>
          )}
          {list.data && list.data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Typ</TableHead>
                  <TableHead>Person</TableHead>
                  <TableHead>Bestellt</TableHead>
                  <TableHead>Bis</TableHead>
                  <TableHead>Aktiv?</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {list.data.results.map((b) => (
                  <TableRow key={b.id}>
                    <TableCell>{b.typ}</TableCell>
                    <TableCell>{b.person_name}</TableCell>
                    <TableCell className="text-xs">{b.bestellt_am}</TableCell>
                    <TableCell className="text-xs">{b.bestellt_bis || "unbefristet"}</TableCell>
                    <TableCell>{b.aktiv ? "✓" : "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
