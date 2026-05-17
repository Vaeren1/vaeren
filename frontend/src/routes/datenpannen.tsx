/**
 * Datenpannen-Register (DSGVO Art. 33/34).
 *
 * Liste mit Frist-Indikator (rot wenn <24h bis 72-h-Frist), CTA „Neue Datenpanne".
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
import { listDatenpannen, type DatenpanneListItem } from "@/lib/api/datenpannen";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

const ART_LABEL: Record<string, string> = {
  verlust_geraet: "Verlust/Diebstahl",
  phishing: "Phishing",
  ransomware: "Ransomware",
  fehlversand: "Fehlversand",
  unberechtigter_zugriff: "Unberechtigter Zugriff",
  konfigurationsfehler: "Konfig-Fehler",
  systemausfall: "Systemausfall",
  insider: "Insider",
  sonstiges: "Sonstiges",
};

const STATUS_LABEL: Record<string, string> = {
  entdeckt: "Entdeckt",
  bewertet: "Bewertet",
  gemeldet: "Gemeldet",
  abgeschlossen: "Abgeschlossen",
  nicht_meldepflichtig: "Nicht meldepfl.",
};

function fristBadge(stunden: number, gemeldet: boolean) {
  if (gemeldet) return <span className="text-emerald-700">erfüllt</span>;
  if (stunden < 0) return <span className="text-red-700 font-semibold">überfällig {Math.abs(Math.round(stunden))} h</span>;
  if (stunden < 24) return <span className="text-red-700">{Math.round(stunden)} h</span>;
  if (stunden < 48) return <span className="text-amber-700">{Math.round(stunden)} h</span>;
  return <span className="text-emerald-700">{Math.round(stunden)} h</span>;
}

export function DatenpannenListPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["datenpannen"],
    queryFn: listDatenpannen,
  });
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Datenpannen-Register</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            DSGVO Art. 33: 72-Stunden-Meldefrist an die Aufsichtsbehörde.
          </p>
        </div>
        <Button asChild>
          <Link to="/datenpannen/neu">+ Neue Datenpanne erfassen</Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground">
            Bisher sind keine Datenpannen erfasst. Wenn das so bleibt — gut. Im Fall der
            Fälle: <Link to="/datenpannen/neu" className="underline">jetzt erfassen</Link>.
          </p>
        )}
        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Art</TableHead>
                <TableHead>Risiko</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Betroffene</TableHead>
                <TableHead className="text-right">72-h-Frist</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((p: DatenpanneListItem) => (
                <TableRow key={p.id}>
                  <TableCell>
                    <Link to={`/datenpannen/${p.id}`} className="underline">
                      {p.titel}
                    </Link>
                  </TableCell>
                  <TableCell>{ART_LABEL[p.art] ?? p.art}</TableCell>
                  <TableCell>{p.risiko || "–"}</TableCell>
                  <TableCell>{STATUS_LABEL[p.status] ?? p.status}</TableCell>
                  <TableCell>{p.anzahl_betroffene_geschaetzt ?? "?"}</TableCell>
                  <TableCell className="text-right">
                    {fristBadge(p.stunden_bis_meldefrist, !!p.behoerde_gemeldet_am)}
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
