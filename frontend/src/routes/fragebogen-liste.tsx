/**
 * OEM-Fragebogen — Übersichtsliste (Feature 4, G1).
 *
 * Listet alle hochgeladenen Fragebögen mit Status + Tier + Fragen-Anzahl.
 * CTA „Fragebogen hochladen" führt in die Upload-Seite, ein Klick auf die
 * Zeile in den seiten-basierten Review.
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
  type FragebogenListItem,
  type FragebogenStatus,
  fragebogen,
} from "@/lib/api/fragebogen";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

const STATUS_LABEL: Record<FragebogenStatus, string> = {
  hochgeladen: "Hochgeladen",
  analysiert: "Analysiert",
  vorgeschlagen: "Vorschläge erstellt",
  in_review: "In Prüfung",
  exportiert: "Exportiert",
  fehler: "Fehler",
};

const STATUS_CLASS: Record<FragebogenStatus, string> = {
  hochgeladen: "text-slate-600",
  analysiert: "text-sky-700",
  vorgeschlagen: "text-sky-700",
  in_review: "text-amber-700",
  exportiert: "text-emerald-700 font-medium",
  fehler: "text-red-700 font-semibold",
};

function statusBadge(status: FragebogenStatus) {
  return (
    <span className={STATUS_CLASS[status] ?? "text-slate-600"}>
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

export function FragebogenListePage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["fragebogen", "liste"],
    queryFn: fragebogen.liste,
  });

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>OEM-Fragebögen</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Laden Sie einen Lieferanten-Fragebogen hoch. Vaeren schlägt
            Antworten aus Ihren Firmendaten vor — Sie prüfen seitenweise und
            attestieren.
          </p>
        </div>
        <Button asChild>
          <Link to="/fragebogen/upload">+ Fragebogen hochladen</Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground">
            Noch keine Fragebögen.{" "}
            <Link to="/fragebogen/upload" className="underline">
              Jetzt den ersten hochladen
            </Link>
            .
          </p>
        )}
        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Datei</TableHead>
                <TableHead>OEM</TableHead>
                <TableHead>Tier</TableHead>
                <TableHead>Fragen</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Attestiert</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((f: FragebogenListItem) => (
                <TableRow key={f.id}>
                  <TableCell>
                    <Link
                      to={`/fragebogen/${f.id}/review`}
                      className="underline"
                    >
                      {f.dateiname}
                    </Link>
                  </TableCell>
                  <TableCell>{f.quelle_oem || "–"}</TableCell>
                  <TableCell>Tier {f.tier}</TableCell>
                  <TableCell>{f.fragen_anzahl}</TableCell>
                  <TableCell>{statusBadge(f.status)}</TableCell>
                  <TableCell className="text-right">
                    {f.final_attestiert ? (
                      <span className="text-emerald-700">✓</span>
                    ) : (
                      <span className="text-muted-foreground">–</span>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
