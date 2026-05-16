/**
 * Kurs-Bibliothek (intern). Listet alle im Tenant verfügbaren Kurse —
 * Standard-Katalog + ggf. selbst angelegte. Klick auf Titel zeigt
 * Modul-Inhalte + Quizfragen mit markierten korrekten Antworten.
 */
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useKursList } from "@/lib/api/schulungen";
import { Link } from "react-router-dom";

export function KurseListPage() {
  const { data, isLoading, isError } = useKursList();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Kurs-Bibliothek</CardTitle>
        <CardDescription>
          Alle Pflicht-Kurse, die in diesem Tenant verfügbar sind. Klick auf den
          Titel öffnet Lerninhalte + Quizfragen für die redaktionelle
          Vorprüfung. Mitarbeiter:innen sehen dieselben Inhalte später beim Quiz
          — aber ohne die Markierung der korrekten Antwort.
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Module</TableHead>
                <TableHead>Fragen</TableHead>
                <TableHead>Gültigkeit</TableHead>
                <TableHead>Bestehensschwelle</TableHead>
                <TableHead>Aktiv</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((k) => (
                <TableRow key={k.id}>
                  <TableCell>
                    <Link
                      to={`/kurse/${k.id}`}
                      className="font-medium underline"
                    >
                      {k.titel}
                    </Link>
                  </TableCell>
                  <TableCell>{k.module.length}</TableCell>
                  <TableCell>{k.fragen_anzahl}</TableCell>
                  <TableCell>{k.gueltigkeit_monate} Mo.</TableCell>
                  <TableCell>{k.min_richtig_prozent} %</TableCell>
                  <TableCell>{k.aktiv ? "ja" : "nein"}</TableCell>
                </TableRow>
              ))}
              {data.results.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6}>
                    Noch keine Kurse angelegt. Hinweis: das Management-Command{" "}
                    <code>seed_kurs_katalog</code> seedet 20 Standard-Kurse.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
