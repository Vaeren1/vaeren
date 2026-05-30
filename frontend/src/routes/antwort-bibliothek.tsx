/**
 * Antwort-Bibliothek (Feature 4, G3).
 *
 * Kuratierbarer Wissensspeicher: Liste der Einträge (kanonische Frage,
 * Antwort, Kategorie, Verwendungs-Zähler) mit Anlegen/Editieren/Löschen via
 * dem `AntwortBibliothekViewSet`-CRUD. Diese Einträge sind Quelle Nr. 1 der
 * Antwort-Engine.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { type BibliothekEintrag, bibliothek } from "@/lib/api/fragebogen";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

interface FormState {
  frage_kanonisch: string;
  antwort_text: string;
  kategorie: string;
}

const LEER: FormState = {
  frage_kanonisch: "",
  antwort_text: "",
  kategorie: "",
};

export function AntwortBibliothekPage() {
  const qc = useQueryClient();
  const [offen, setOffen] = useState(false);
  const [bearbeiteId, setBearbeiteId] = useState<number | null>(null);
  const [form, setForm] = useState<FormState>(LEER);

  const { data, isLoading, isError } = useQuery({
    queryKey: ["antwort-bibliothek"],
    queryFn: () => bibliothek.liste(),
  });

  function invalidate() {
    qc.invalidateQueries({ queryKey: ["antwort-bibliothek"] });
  }

  const speichern = useMutation({
    mutationFn: () =>
      bearbeiteId === null
        ? bibliothek.anlegen(form)
        : bibliothek.aktualisieren(bearbeiteId, form),
    onSuccess: () => {
      invalidate();
      setOffen(false);
      setForm(LEER);
      setBearbeiteId(null);
    },
  });

  const loeschen = useMutation({
    mutationFn: (id: number) => bibliothek.loeschen(id),
    onSuccess: invalidate,
  });

  function neu() {
    setBearbeiteId(null);
    setForm(LEER);
    setOffen(true);
  }

  function bearbeiten(e: BibliothekEintrag) {
    setBearbeiteId(e.id);
    setForm({
      frage_kanonisch: e.frage_kanonisch,
      antwort_text: e.antwort_text,
      kategorie: e.kategorie ?? "",
    });
    setOffen(true);
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>Antwort-Bibliothek</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Wiederverwendbare Standard-Antworten. Wächst automatisch mit jeder
            attestierten Fragebogen-Antwort und ist hier kuratierbar.
          </p>
        </div>
        <Button type="button" onClick={neu}>
          + Neuer Eintrag
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {isError && <p className="text-destructive">Fehler beim Laden.</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground">
            Noch keine Einträge. Sie entstehen automatisch beim Attestieren von
            Fragebögen — oder legen Sie hier manuell welche an.
          </p>
        )}
        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Frage (kanonisch)</TableHead>
                <TableHead>Antwort</TableHead>
                <TableHead>Kategorie</TableHead>
                <TableHead className="text-right">Verwendungen</TableHead>
                <TableHead className="text-right">Aktionen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((e) => (
                <TableRow key={e.id}>
                  <TableCell className="max-w-xs align-top">
                    {e.frage_kanonisch}
                  </TableCell>
                  <TableCell className="max-w-md align-top text-muted-foreground">
                    {e.antwort_text}
                  </TableCell>
                  <TableCell className="align-top">
                    {e.kategorie || "–"}
                  </TableCell>
                  <TableCell className="text-right align-top">
                    {e.verwendungs_count}
                  </TableCell>
                  <TableCell className="text-right align-top">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        type="button"
                        onClick={() => bearbeiten(e)}
                      >
                        Bearbeiten
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        type="button"
                        disabled={loeschen.isPending}
                        onClick={() => {
                          if (
                            window.confirm(
                              `Eintrag „${e.frage_kanonisch.slice(0, 40)}…" wirklich löschen?`,
                            )
                          ) {
                            loeschen.mutate(e.id);
                          }
                        }}
                      >
                        Löschen
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      <Dialog open={offen} onOpenChange={setOffen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {bearbeiteId === null ? "Neuer Eintrag" : "Eintrag bearbeiten"}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="frage">Frage (kanonisch)</Label>
              <Textarea
                id="frage"
                rows={2}
                value={form.frage_kanonisch}
                onChange={(e) =>
                  setForm({ ...form, frage_kanonisch: e.target.value })
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="antwort">Antwort</Label>
              <Textarea
                id="antwort"
                rows={4}
                value={form.antwort_text}
                onChange={(e) =>
                  setForm({ ...form, antwort_text: e.target.value })
                }
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="kategorie">Kategorie (optional)</Label>
              <Input
                id="kategorie"
                value={form.kategorie}
                onChange={(e) =>
                  setForm({ ...form, kategorie: e.target.value })
                }
              />
            </div>
            {speichern.isError && (
              <p className="text-sm text-destructive">
                Speichern fehlgeschlagen.
              </p>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              type="button"
              onClick={() => setOffen(false)}
            >
              Abbrechen
            </Button>
            <Button
              type="button"
              disabled={
                !form.frage_kanonisch ||
                !form.antwort_text ||
                speichern.isPending
              }
              onClick={() => speichern.mutate()}
            >
              {speichern.isPending ? "Speichere …" : "Speichern"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
