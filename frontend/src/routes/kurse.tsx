/**
 * Kurs-Bibliothek (intern). Gruppiert: oben „Eigene Kurse" (themenübergreifend),
 * darunter Vaeren-Standard nach Kategorie (collapsible). „+ Neuer Kurs" oben
 * rechts; Edit/Löschen-Icons pro eigenem Kurs.
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
import {
  KATEGORIE_LABEL,
  KATEGORIE_ORDER,
  type Kategorie,
  type Kurs,
  useDeleteKurs,
  useKursList,
} from "@/lib/api/schulungen";
import {
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Flame,
  Folder,
  HardHat,
  Leaf,
  Pencil,
  Plus,
  Scale,
  Shield,
  Trash2,
} from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";

const MODUS_LABEL: Record<string, string> = {
  quiz: "Quiz",
  kenntnisnahme: "Kenntnisnahme",
  kenntnisnahme_lesezeit: "Kenntnisn. + Zeit",
};

const KATEGORIE_ICON: Record<Kategorie, typeof HardHat> = {
  arbeitsschutz: HardHat,
  brandschutz: Flame,
  gefahrstoffe: AlertTriangle,
  datenschutz: Shield,
  compliance: Scale,
  umwelt: Leaf,
  sonstiges: Folder,
};

export function KurseListPage() {
  const { data, isLoading, isError } = useKursList();
  const del = useDeleteKurs();
  const navigate = useNavigate();
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});

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

  const toggle = (key: string) =>
    setCollapsed((s) => ({ ...s, [key]: !s[key] }));

  const eigene: Kurs[] = (data?.results ?? []).filter(
    (k) => !k.ist_standardkatalog,
  );
  const standardByKat = new Map<Kategorie, Kurs[]>();
  for (const k of data?.results ?? []) {
    if (!k.ist_standardkatalog) continue;
    const list = standardByKat.get(k.kategorie) ?? [];
    list.push(k);
    standardByKat.set(k.kategorie, list);
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-6">
          <div className="max-w-2xl">
            <CardTitle>Kurs-Bibliothek</CardTitle>
            <CardDescription>
              Eigene Kurse stehen oben. Darunter folgen die Vaeren-Standard-
              Kurse nach Themenbereich gruppiert — Klick auf den Themen-Header
              klappt die Tabelle ein/aus.
            </CardDescription>
          </div>
          <Button onClick={() => navigate("/kurse/neu")} className="shrink-0">
            <Plus className="mr-1 h-4 w-4" /> Neuer Kurs
          </Button>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Lade …</p>}
          {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <button
              type="button"
              onClick={() => toggle("eigene")}
              className="flex w-full items-center gap-2 text-left"
            >
              {collapsed.eigene ? (
                <ChevronRight className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
              <CardTitle className="text-base">
                Eigene Kurse{" "}
                <span className="text-sm font-normal text-muted-foreground">
                  ({eigene.length})
                </span>
              </CardTitle>
            </button>
          </CardHeader>
          {!collapsed.eigene && (
            <CardContent>
              {eigene.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Noch keine eigenen Kurse angelegt. Über „+ Neuer Kurs" oben
                  rechts starten.
                </p>
              ) : (
                <KursTable
                  kurse={eigene}
                  onDelete={handleDelete}
                  onEdit={(id) => navigate(`/kurse/${id}/bearbeiten`)}
                />
              )}
            </CardContent>
          )}
        </Card>
      )}

      {data &&
        KATEGORIE_ORDER.map((kat) => {
          const kurse = standardByKat.get(kat) ?? [];
          if (kurse.length === 0) return null;
          const Icon = KATEGORIE_ICON[kat];
          const key = `std-${kat}`;
          return (
            <Card key={kat}>
              <CardHeader>
                <button
                  type="button"
                  onClick={() => toggle(key)}
                  className="flex w-full items-center gap-2 text-left"
                >
                  {collapsed[key] ? (
                    <ChevronRight className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                  <Icon className="h-4 w-4 text-muted-foreground" />
                  <CardTitle className="text-base">
                    {KATEGORIE_LABEL[kat]}{" "}
                    <span className="text-sm font-normal text-muted-foreground">
                      ({kurse.length})
                    </span>
                  </CardTitle>
                </button>
              </CardHeader>
              {!collapsed[key] && (
                <CardContent>
                  <KursTable kurse={kurse} />
                </CardContent>
              )}
            </Card>
          );
        })}
    </div>
  );
}

function KursTable({
  kurse,
  onEdit,
  onDelete,
}: {
  kurse: Kurs[];
  onEdit?: (id: number) => void;
  onDelete?: (id: number, titel: string) => void;
}) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Titel</TableHead>
          <TableHead>Modus</TableHead>
          <TableHead>Module</TableHead>
          <TableHead>Fragen (Quiz/Pool)</TableHead>
          <TableHead>Gültig</TableHead>
          <TableHead>Zertifikat</TableHead>
          <TableHead>Aktiv</TableHead>
          {(onEdit || onDelete) && <TableHead className="w-24" />}
        </TableRow>
      </TableHeader>
      <TableBody>
        {kurse.map((k) => (
          <TableRow key={k.id}>
            <TableCell>
              <Link to={`/kurse/${k.id}`} className="font-medium underline">
                {k.titel}
              </Link>
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
            {(onEdit || onDelete) && (
              <TableCell>
                <div className="flex gap-1">
                  {onEdit && (
                    <Button
                      size="icon"
                      variant="ghost"
                      aria-label="Bearbeiten"
                      onClick={() => onEdit(k.id)}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                  )}
                  {onDelete && (
                    <Button
                      size="icon"
                      variant="ghost"
                      aria-label="Löschen"
                      onClick={() => onDelete(k.id, k.titel)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  )}
                </div>
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
