/**
 * Audit-Liste mit CREATE-Modal. Detail-View liegt in AuditDetail.tsx.
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
  createAudit,
  listAudits,
  listControls,
  type InternesAudit,
  type Iso27001ControlListItem,
} from "@/lib/api/iso27001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";

function statusBadge(status: InternesAudit["status"]): string {
  if (status === "geplant") return "bg-slate-100 text-slate-700 border-slate-300";
  if (status === "laufend") return "bg-amber-100 text-amber-800 border-amber-300";
  return "bg-emerald-100 text-emerald-800 border-emerald-300";
}

export function Iso27001Audits() {
  const qc = useQueryClient();
  const { data: audits, isLoading } = useQuery({
    queryKey: ["iso27001-audits"],
    queryFn: listAudits,
  });
  const { data: controls } = useQuery({
    queryKey: ["iso27001-controls"],
    queryFn: () => listControls(),
  });
  const [showCreate, setShowCreate] = useState(false);

  const createMut = useMutation({
    mutationFn: createAudit,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-audits"] });
      toast.success("Audit angelegt.");
      setShowCreate(false);
    },
    onError: (e: unknown) => {
      toast.error(e instanceof Error ? e.message : "Anlegen fehlgeschlagen");
    },
  });

  return (
    <Card>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div>
            <CardTitle>Internes Audit-Programm (ISO 9.2)</CardTitle>
            <p className="mt-1 text-sm text-muted-foreground">
              Plant + dokumentiert interne ISMS-Audits inkl. Findings + Maßnahmen.
            </p>
          </div>
          <Button onClick={() => setShowCreate(true)}>+ Audit anlegen</Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p>Lade …</p>
        ) : !audits || audits.results.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Noch kein Audit geplant.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Zeitraum</TableHead>
                <TableHead>Auditor</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Findings</TableHead>
                <TableHead>Aktionen</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {audits.results.map((a) => (
                <TableRow key={a.id}>
                  <TableCell className="font-medium">{a.titel}</TableCell>
                  <TableCell className="text-xs">
                    {a.auditzeitraum_von} → {a.auditzeitraum_bis}
                  </TableCell>
                  <TableCell>{a.auditor}</TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex rounded border px-2 py-0.5 text-xs ${statusBadge(a.status)}`}
                    >
                      {a.status}
                    </span>
                  </TableCell>
                  <TableCell>{a.findings_count}</TableCell>
                  <TableCell>
                    <Link
                      to={`/iso27001/audits/${a.id}`}
                      className="text-sm underline"
                    >
                      Details
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>

      {showCreate && (
        <AuditCreateForm
          controls={controls?.results ?? []}
          onCancel={() => setShowCreate(false)}
          onSubmit={(payload) => createMut.mutate(payload)}
          isPending={createMut.isPending}
        />
      )}
    </Card>
  );
}

function AuditCreateForm({
  controls,
  onCancel,
  onSubmit,
  isPending,
}: {
  controls: Iso27001ControlListItem[];
  onCancel: () => void;
  onSubmit: (payload: Partial<InternesAudit>) => void;
  isPending: boolean;
}) {
  const [titel, setTitel] = useState("");
  const [von, setVon] = useState(new Date().toISOString().slice(0, 10));
  const [bis, setBis] = useState(new Date().toISOString().slice(0, 10));
  const [auditor, setAuditor] = useState("");
  const [selectedControls, setSelectedControls] = useState<Set<number>>(
    new Set(),
  );

  function toggleControl(id: number) {
    setSelectedControls((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 overflow-y-auto py-8">
      <form
        className="w-[720px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            titel,
            auditzeitraum_von: von,
            auditzeitraum_bis: bis,
            auditor,
            geprueft_controls: Array.from(selectedControls),
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">Neues internes Audit</h2>
        <div className="space-y-3">
          <div>
            <Label>Titel</Label>
            <Input
              value={titel}
              onChange={(e) => setTitel(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label>Von</Label>
              <Input
                type="date"
                value={von}
                onChange={(e) => setVon(e.target.value)}
                required
              />
            </div>
            <div>
              <Label>Bis</Label>
              <Input
                type="date"
                value={bis}
                onChange={(e) => setBis(e.target.value)}
                required
              />
            </div>
          </div>
          <div>
            <Label>Auditor</Label>
            <Input
              value={auditor}
              onChange={(e) => setAuditor(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Geprüfte Controls ({selectedControls.size} ausgewählt)</Label>
            <div className="mt-1 max-h-64 overflow-y-auto rounded border p-2 text-xs">
              {controls.map((c) => (
                <label
                  key={c.id}
                  className="flex items-center gap-2 py-0.5 cursor-pointer hover:bg-muted/40 rounded px-1"
                >
                  <input
                    type="checkbox"
                    checked={selectedControls.has(c.id)}
                    onChange={() => toggleControl(c.id)}
                  />
                  <span className="font-mono">{c.code}</span>
                  <span className="text-muted-foreground">{c.name}</span>
                </label>
              ))}
            </div>
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
