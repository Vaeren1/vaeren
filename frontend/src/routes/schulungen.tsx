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
import { useWelleList } from "@/lib/api/schulungen";
import { Link } from "react-router-dom";

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf",
  sent: "Versendet",
  in_progress: "In Bearbeitung",
  completed: "Abgeschlossen",
};

export function SchulungenListPage() {
  const { data, isLoading, isError } = useWelleList();
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Schulungs-Wellen</CardTitle>
        <Button asChild>
          <Link to="/schulungen/neu">+ Neue Welle</Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Kurs</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Deadline</TableHead>
                <TableHead>Mitarbeiter</TableHead>
                <TableHead>Bestanden</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((w) => {
                const total = w.tasks.length;
                const bestanden = w.tasks.filter(
                  (t) => t.bestanden === true,
                ).length;
                return (
                  <TableRow key={w.id}>
                    <TableCell>
                      <Link
                        to={`/schulungen/${w.id}`}
                        className="font-medium underline"
                      >
                        {w.titel}
                      </Link>
                    </TableCell>
                    <TableCell>{w.kurs_titel}</TableCell>
                    <TableCell>{STATUS_LABEL[w.status] ?? w.status}</TableCell>
                    <TableCell>{w.deadline}</TableCell>
                    <TableCell>{total}</TableCell>
                    <TableCell>
                      {total > 0 ? `${bestanden} / ${total}` : "—"}
                    </TableCell>
                  </TableRow>
                );
              })}
              {data.results.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6}>Keine Wellen vorhanden.</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
