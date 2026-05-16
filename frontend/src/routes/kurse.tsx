/**
 * Kurs-Bibliothek (intern). Listet alle im Tenant verfügbaren Kurse —
 * Standard-Katalog + ggf. selbst angelegte. Klick auf Titel zeigt Modul-
 * Inhalte + Quizfragen. „+ Neuer Kurs" öffnet das Anlege-Form. Pro
 * eigenem Kurs gibt es Edit/Löschen-Icons.
 */
import { Button } from "@/components/ui/button";
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
import { useDeleteKurs, useKursList } from "@/lib/api/schulungen";
import { Pencil, Plus, Trash2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

const MODUS_LABEL: Record<string, string> = {
  quiz: "Quiz",
  kenntnisnahme: "Kenntnisnahme",
  kenntnisnahme_lesezeit: "Kenntnisn. + Zeit",
};

export function KurseListPage() {
  const { data, isLoading, isError } = useKursList();
  const del = useDeleteKurs();
  const navigate = useNavigate();

  const handleDelete = (id: number, titel: string) => {
    if (!window.confirm(`Kurs „${titel}" wirklich löschen?`)) return;
    del.mutate(id, {
      onSuccess: () => toast.success("Kurs gelöscht."),
      onError: (err) => {
        const msg =
          err.body && typeof err.body === "object"
            ? Object.values(err.body as Record<string, unknown>)
                .flat()
                .join(" ")
            : "Löschen fehlgeschlagen.";
        toast.error(String(msg));
      },
    });
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between">
        <div>
          <CardTitle>Kurs-Bibliothek</CardTitle>
          <CardDescription>
            Alle Pflicht-Kurse, die in diesem Tenant verfügbar sind. Standard-
            Katalog-Kurse können angesehen, aber nicht editiert werden. Eigene
            Kurse legen Sie über „+ Neuer Kurs" an.
          </CardDescription>
        </div>
        <Button onClick={() => navigate("/kurse/neu")}>
          <Plus className="mr-1 h-4 w-4" /> Neuer Kurs
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
                <TableHead>Eigentümer</TableHead>
                <TableHead>Modus</TableHead>
                <TableHead>Module</TableHead>
                <TableHead>Fragen (Quiz/Pool)</TableHead>
                <TableHead>Gültig</TableHead>
                <TableHead>Zertifikat</TableHead>
                <TableHead>Aktiv</TableHead>
                <TableHead className="w-24" />
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
                  <TableCell className="text-xs">
                    {k.ist_standardkatalog ? (
                      <span className="rounded bg-slate-100 px-2 py-0.5">
                        Vaeren-Standard
                      </span>
                    ) : (
                      <span className="rounded bg-emerald-50 px-2 py-0.5 text-emerald-900">
                        Eigener
                      </span>
                    )}
                  </TableCell>
                  <TableCell>
                    {MODUS_LABEL[k.quiz_modus] ?? k.quiz_modus}
                  </TableCell>
                  <TableCell>{k.module.length}</TableCell>
                  <TableCell>
                    {k.quiz_modus === "quiz"
                      ? `${k.fragen_pro_quiz} / ${k.fragen_pool_groesse}`
                      : "—"}
                  </TableCell>
                  <TableCell>{k.gueltigkeit_monate} Mo.</TableCell>
                  <TableCell>{k.zertifikat_aktiv ? "ja" : "nein"}</TableCell>
                  <TableCell>{k.aktiv ? "ja" : "nein"}</TableCell>
                  <TableCell>
                    {!k.ist_standardkatalog && (
                      <div className="flex gap-1">
                        <Button
                          size="icon"
                          variant="ghost"
                          aria-label="Bearbeiten"
                          onClick={() =>
                            navigate(`/kurse/${k.id}/bearbeiten`)
                          }
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          aria-label="Löschen"
                          onClick={() => handleDelete(k.id, k.titel)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
              {data.results.length === 0 && (
                <TableRow>
                  <TableCell colSpan={9}>
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
