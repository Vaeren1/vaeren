/**
 * Betriebsanweisungs-Bibliothek mit Versions-Anzeige.
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
import { listBetriebsanweisungen } from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";

export function BetriebsanweisungBibliothekPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["as-ba"],
    queryFn: listBetriebsanweisungen,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Betriebsanweisungen</CardTitle>
        <p className="text-sm text-muted-foreground">
          BetrSichV §12 / GefStoffV §14. Aushang-Pflicht.
        </p>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade…</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Bisher keine Betriebsanweisungen erfasst.
          </p>
        )}
        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Typ</TableHead>
                <TableHead>Versionen</TableHead>
                <TableHead>Aktuelle Version</TableHead>
                <TableHead>PDF</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((ba) => {
                const akt = ba.versionen.find((v) => v.id === ba.aktuelle_version);
                return (
                  <TableRow key={ba.id}>
                    <TableCell className="font-medium">{ba.titel}</TableCell>
                    <TableCell>{ba.typ}</TableCell>
                    <TableCell>{ba.versionen.length}</TableCell>
                    <TableCell>{akt ? `v${akt.version}` : "—"}</TableCell>
                    <TableCell>
                      {akt?.pdf_file ? (
                        <a className="underline" href={akt.pdf_file} target="_blank" rel="noreferrer">
                          PDF
                        </a>
                      ) : (
                        "—"
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
