/**
 * Internes Bearbeiter-Dashboard: Liste aller HinSchG-Meldungen.
 * Permission: GF (lesen) + Compliance-Beauftragter (lesen+bearbeiten).
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
import { useMeldungList } from "@/lib/api/hinschg";
import { Link } from "react-router-dom";

export function MeldungenListPage() {
  const { data, isLoading, isError } = useMeldungList();

  return (
    <Card>
      <CardHeader>
        <CardTitle>HinSchG-Meldungen</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && (
          <p className="text-destructive">
            Keine Berechtigung oder Fehler beim Laden.
          </p>
        )}
        {data && data.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Bisher keine Meldungen eingegangen.
          </p>
        )}
        {data && data.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Eingegangen</TableHead>
                <TableHead>Titel</TableHead>
                <TableHead>Anonym</TableHead>
                <TableHead>Kategorie</TableHead>
                <TableHead>Schweregrad</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Frist (3M)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((m) => (
                <TableRow key={m.id}>
                  <TableCell>
                    {new Date(m.eingegangen_am).toLocaleDateString("de-DE")}
                  </TableCell>
                  <TableCell>
                    <Link
                      to={`/meldungen/${m.id}`}
                      className="font-medium underline"
                    >
                      {m.titel}
                    </Link>
                  </TableCell>
                  <TableCell>{m.anonym ? "ja" : "nein"}</TableCell>
                  <TableCell>{m.kategorie || "—"}</TableCell>
                  <TableCell>{m.schweregrad || "—"}</TableCell>
                  <TableCell>{m.status_display}</TableCell>
                  <TableCell>{m.rueckmeldung_faellig_bis}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
