/**
 * Management-Review-Liste mit CREATE-Modal.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
import {
  createMgtReview,
  listMgtReviews,
  type ManagementReview,
} from "@/lib/api/iso27001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

function statusBadge(status: ManagementReview["status"]): string {
  if (status === "genehmigt")
    return "bg-emerald-100 text-emerald-800 border-emerald-300";
  if (status === "durchgefuehrt")
    return "bg-amber-100 text-amber-800 border-amber-300";
  return "bg-slate-100 text-slate-700 border-slate-300";
}

export function Iso27001ManagementReview() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["iso27001-mgt-reviews"],
    queryFn: listMgtReviews,
  });
  const [showCreate, setShowCreate] = useState(false);

  const createMut = useMutation({
    mutationFn: createMgtReview,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-mgt-reviews"] });
      toast.success("Review angelegt.");
      setShowCreate(false);
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Anlegen fehlgeschlagen"),
  });

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>Management-Review (ISO 9.3)</CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              Jährlicher Review durch GF. Inputs (Audit-Ergebnisse, Findings,
              Risiken, Performance) werden automatisch aus den letzten 12
              Monaten vorbefüllt.
            </p>
          </div>
          <Button onClick={() => setShowCreate(true)}>+ Review anlegen</Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p>Lade …</p>
        ) : !data || data.results.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Noch kein Review erstellt.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Jahr</TableHead>
                <TableHead>Durchgeführt am</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Aktionen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((m) => (
                <TableRow key={m.id}>
                  <TableCell className="font-medium">{m.review_jahr}</TableCell>
                  <TableCell className="text-xs">
                    {m.durchgefuehrt_am ?? "—"}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex rounded border px-2 py-0.5 text-xs ${statusBadge(m.status)}`}
                    >
                      {m.status}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Link
                      to={`/iso27001/management-review/${m.id}`}
                      className="text-sm underline"
                    >
                      Öffnen
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      {showCreate && (
        <ReviewCreateForm
          onCancel={() => setShowCreate(false)}
          onSubmit={(payload) => createMut.mutate(payload)}
          isPending={createMut.isPending}
        />
      )}
    </Card>
  );
}

function ReviewCreateForm({
  onCancel,
  onSubmit,
  isPending,
}: {
  onCancel: () => void;
  onSubmit: (payload: Partial<ManagementReview>) => void;
  isPending: boolean;
}) {
  const [jahr, setJahr] = useState(new Date().getFullYear());
  const [datum, setDatum] = useState<string>("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[480px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            review_jahr: jahr,
            durchgefuehrt_am: datum || null,
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">Neuer Management-Review</h2>
        <div className="space-y-3">
          <div>
            <Label>Jahr</Label>
            <Input
              type="number"
              value={jahr}
              onChange={(e) => setJahr(Number(e.target.value))}
              required
            />
          </div>
          <div>
            <Label>Durchgeführt am (optional)</Label>
            <Input
              type="date"
              value={datum}
              onChange={(e) => setDatum(e.target.value)}
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Anlegen
          </Button>
        </div>
      </form>
    </div>
  );
}
