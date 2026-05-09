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
  ROLES_THAT_CAN_EDIT_MITARBEITER,
  useDeleteMitarbeiter,
  useMitarbeiterList,
} from "@/lib/api/mitarbeiter";
import { useAuthStore } from "@/lib/stores/auth-store";
import { Link } from "react-router-dom";
import { toast } from "sonner";

export function MitarbeiterListPage() {
  const role = useAuthStore((s) => s.user?.tenant_role);
  const canEdit = role ? ROLES_THAT_CAN_EDIT_MITARBEITER.has(role) : false;
  const { data, isLoading, isError } = useMitarbeiterList();
  const del = useDeleteMitarbeiter();

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Mitarbeiter</CardTitle>
        {canEdit && (
          <Button asChild>
            <Link to="/mitarbeiter/neu">+ Neuer Mitarbeiter</Link>
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>E-Mail</TableHead>
                <TableHead>Abteilung</TableHead>
                <TableHead>Aktiv</TableHead>
                {canEdit && <TableHead className="w-32">Aktionen</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((m) => (
                <TableRow key={m.id}>
                  <TableCell>
                    {m.vorname} {m.nachname}
                  </TableCell>
                  <TableCell>{m.email}</TableCell>
                  <TableCell>{m.abteilung}</TableCell>
                  <TableCell>{m.aktiv ? "ja" : "nein"}</TableCell>
                  {canEdit && (
                    <TableCell>
                      <div className="flex gap-2">
                        <Button asChild size="sm" variant="outline">
                          <Link to={`/mitarbeiter/${m.id}/bearbeiten`}>
                            Bearbeiten
                          </Link>
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => {
                            if (
                              !window.confirm(
                                `Mitarbeiter ${m.vorname} ${m.nachname} wirklich löschen?`,
                              )
                            )
                              return;
                            del.mutate(m.id, {
                              onSuccess: () => toast.success("Gelöscht."),
                              onError: () =>
                                toast.error("Löschen fehlgeschlagen."),
                            });
                          }}
                        >
                          Löschen
                        </Button>
                      </div>
                    </TableCell>
                  )}
                </TableRow>
              ))}
              {data.results.length === 0 && (
                <TableRow>
                  <TableCell colSpan={canEdit ? 5 : 4}>
                    Keine Mitarbeiter angelegt.
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
