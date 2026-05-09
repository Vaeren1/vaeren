import { useParams } from "react-router-dom";
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
import { useWelle } from "@/lib/api/schulungen";

const STATUS_LABEL: Record<string, string> = {
  draft: "Entwurf",
  sent: "Versendet",
  in_progress: "In Bearbeitung",
  completed: "Abgeschlossen",
};

export function WelleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number.parseInt(id, 10) : undefined;
  const { data, isLoading } = useWelle(numericId);

  if (isLoading || !data) return <p>Lade …</p>;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>{data.titel}</CardTitle>
          <CardDescription>
            Kurs: {data.kurs_titel} · Status: {STATUS_LABEL[data.status]} ·
            Deadline: {data.deadline}
            {data.versendet_am && ` · Versendet: ${data.versendet_am}`}
          </CardDescription>
        </CardHeader>
        {data.einleitungs_text && (
          <CardContent>
            <h3 className="mb-2 text-sm font-medium">Einleitungstext</h3>
            <div className="whitespace-pre-wrap rounded border bg-muted/40 p-3 text-sm">
              {data.einleitungs_text}
            </div>
          </CardContent>
        )}
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Mitarbeiter ({data.tasks.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Abgeschlossen</TableHead>
                <TableHead>Richtig %</TableHead>
                <TableHead>Bestanden</TableHead>
                <TableHead>Ablauf</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.tasks.map((t) => (
                <TableRow key={t.id}>
                  <TableCell>{t.mitarbeiter_name}</TableCell>
                  <TableCell>{t.abgeschlossen_am ?? "—"}</TableCell>
                  <TableCell>
                    {t.richtig_prozent !== null ? `${t.richtig_prozent} %` : "—"}
                  </TableCell>
                  <TableCell>
                    {t.bestanden === null ? "—" : t.bestanden ? "ja" : "nein"}
                  </TableCell>
                  <TableCell>{t.ablauf_datum ?? "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
