/**
 * Arbeitsunfall-Liste — anonymisiert (Klarname nur in Detail-View).
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { listUnfaelle, unfallStatistik, type UnfallSchwere } from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";

const SCHWERE_LABEL: Record<UnfallSchwere, string> = {
  bagatell: "Bagatell",
  leicht: "Leicht",
  meldepflichtig: "Meldepflichtig",
  schwer: "Schwer",
  toedlich: "Tödlich",
  fast_unfall: "Beinahe-Unfall",
};

const SCHWERE_COLOR: Record<UnfallSchwere, string> = {
  bagatell: "text-slate-700",
  leicht: "text-amber-700",
  meldepflichtig: "text-rose-700",
  schwer: "text-rose-800 font-semibold",
  toedlich: "text-red-900 font-bold",
  fast_unfall: "text-sky-700",
};

export function UnfallListPage() {
  const list = useQuery({ queryKey: ["as-unfaelle"], queryFn: listUnfaelle });
  const stat = useQuery({ queryKey: ["as-unfall-stat"], queryFn: unfallStatistik });

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">YTD gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stat.data?.ytd_total ?? "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">YTD meldepfl.</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-rose-700">
              {stat.data?.ytd_meldepflichtig ?? "—"}
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">YTD schwer</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stat.data?.ytd_schwer ?? "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Ausfalltage YTD</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stat.data?.ytd_ausfalltage ?? "—"}</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Arbeitsunfälle</CardTitle>
          <p className="text-xs text-muted-foreground">
            Inhalt verschlüsselt at-rest · DSGVO Art. 9. Klarname nur in Detail-Ansicht.
          </p>
        </CardHeader>
        <CardContent>
          {list.data && list.data.results.length === 0 && (
            <p className="text-muted-foreground text-sm">
              Bisher keine Unfälle erfasst. Im Fall der Fälle: sofort hier eintragen.
            </p>
          )}
          {list.data && list.data.results.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Datum</TableHead>
                  <TableHead>Bereich</TableHead>
                  <TableHead>Schwere</TableHead>
                  <TableHead>Ausfalltage</TableHead>
                  <TableHead>BG-Meldung</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {list.data.results.map((u) => (
                  <TableRow key={u.id}>
                    <TableCell>{new Date(u.datum).toLocaleDateString("de-DE")}</TableCell>
                    <TableCell>{u.arbeitsbereich_name}</TableCell>
                    <TableCell className={SCHWERE_COLOR[u.schwere]}>
                      {SCHWERE_LABEL[u.schwere]}
                    </TableCell>
                    <TableCell>{u.ausfalltage}</TableCell>
                    <TableCell className="text-xs">
                      {u.bg_gemeldet_am
                        ? `gemeldet ${u.bg_gemeldet_am}`
                        : u.bg_meldung_pflicht
                          ? `Frist ${u.bg_meldefrist}`
                          : "—"}
                    </TableCell>
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
