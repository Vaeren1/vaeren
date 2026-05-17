/**
 * SoA-Liste: 38 Annex-A-Controls mit Inline-Edit über Side-Drawer.
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
import {
  KATEGORIE_LABELS,
  STATUS_LABELS,
  listControls,
  upsertControlImplementation,
  type ControlImplementationStatus,
  type ControlListItem,
} from "@/lib/api/iso42001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { toast } from "sonner";

const STATUS_VALUES: ControlImplementationStatus[] = [
  "offen",
  "geplant",
  "umgesetzt",
  "abgeschlossen",
  "nicht_anwendbar",
];

export function Iso42001ControlListPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["iso42001-controls"],
    queryFn: listControls,
  });
  const [filter, setFilter] = useState<string>("");
  const [edit, setEdit] = useState<ControlListItem | null>(null);

  const grouped = useMemo(() => {
    if (!data) return {};
    const g: Record<string, ControlListItem[]> = {};
    for (const c of data) {
      if (filter && c.kategorie !== filter) continue;
      g[c.kategorie] = g[c.kategorie] || [];
      g[c.kategorie].push(c);
    }
    return g;
  }, [data, filter]);

  const saveMut = useMutation({
    mutationFn: upsertControlImplementation,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-controls"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("Control-Status gespeichert.");
      setEdit(null);
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Fehler beim Speichern";
      toast.error(msg);
    },
  });

  function statusBadge(status: ControlImplementationStatus | null) {
    if (status === null) return <span className="text-slate-400">—</span>;
    const color =
      status === "umgesetzt" || status === "abgeschlossen"
        ? "bg-emerald-100 text-emerald-800"
        : status === "geplant"
          ? "bg-amber-100 text-amber-800"
          : status === "nicht_anwendbar"
            ? "bg-slate-100 text-slate-700"
            : "bg-rose-50 text-rose-700";
    return (
      <span className={`rounded-full px-2 py-0.5 text-xs ${color}`}>
        {STATUS_LABELS[status]}
      </span>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Statement of Applicability</h1>
          <p className="text-sm text-muted-foreground">
            38 Annex-A-Controls. Jedes Control muss umgesetzt oder begründet ausgeschlossen werden.
          </p>
        </div>
        <select
          className="rounded border px-3 py-2 text-sm"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
        >
          <option value="">Alle Kategorien</option>
          {Object.entries(KATEGORIE_LABELS).map(([k, l]) => (
            <option key={k} value={k}>
              {l}
            </option>
          ))}
        </select>
      </div>

      {isLoading && <p>Lade …</p>}

      {Object.entries(grouped).map(([kat, items]) => (
        <Card key={kat}>
          <CardHeader>
            <CardTitle>{KATEGORIE_LABELS[kat] ?? kat}</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-20">Code</TableHead>
                  <TableHead>Titel</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Anwendbar</TableHead>
                  <TableHead className="w-24" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((c) => (
                  <TableRow key={c.code}>
                    <TableCell className="font-mono text-xs">{c.code}</TableCell>
                    <TableCell>
                      <div className="font-medium">{c.title_de}</div>
                      <div className="text-xs text-slate-500">{c.description_de}</div>
                    </TableCell>
                    <TableCell>{statusBadge(c.status)}</TableCell>
                    <TableCell>
                      {c.anwendbar === null ? "—" : c.anwendbar ? "Ja" : "Nein"}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button size="sm" variant="outline" onClick={() => setEdit(c)}>
                        Bearbeiten
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      ))}

      {edit && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
          <div className="w-[640px] max-w-full rounded-md bg-white p-6 shadow-xl">
            <div className="mb-4">
              <h2 className="text-lg font-semibold">
                {edit.code} — {edit.title_de}
              </h2>
              <p className="text-xs text-muted-foreground">{edit.description_de}</p>
            </div>
            <ControlEditForm
              initial={edit}
              onCancel={() => setEdit(null)}
              onSave={(payload) =>
                saveMut.mutate({
                  id: edit.implementation_id ?? undefined,
                  control_code: edit.code,
                  ...payload,
                })
              }
              isPending={saveMut.isPending}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function ControlEditForm({
  initial,
  onCancel,
  onSave,
  isPending,
}: {
  initial: ControlListItem;
  onCancel: () => void;
  onSave: (payload: {
    anwendbar: boolean;
    status: ControlImplementationStatus;
    beschreibung: string;
    nicht_anwendbar_begruendung: string;
  }) => void;
  isPending: boolean;
}) {
  const [anwendbar, setAnwendbar] = useState<boolean>(initial.anwendbar ?? true);
  const [status, setStatus] = useState<ControlImplementationStatus>(
    initial.status ?? "offen",
  );
  const [beschreibung, setBeschreibung] = useState(initial.beschreibung ?? "");
  const [begruendung, setBegruendung] = useState(
    initial.nicht_anwendbar_begruendung ?? "",
  );

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSave({
          anwendbar,
          status,
          beschreibung,
          nicht_anwendbar_begruendung: begruendung,
        });
      }}
      className="space-y-3"
    >
      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={anwendbar}
          onChange={(e) => setAnwendbar(e.target.checked)}
        />
        Anwendbar
      </label>
      <div>
        <label className="mb-1 block text-sm">Status</label>
        <select
          className="w-full rounded border px-3 py-2 text-sm"
          value={status}
          onChange={(e) => setStatus(e.target.value as ControlImplementationStatus)}
        >
          {STATUS_VALUES.map((s) => (
            <option key={s} value={s}>
              {STATUS_LABELS[s]}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="mb-1 block text-sm">Umsetzungs-Beschreibung</label>
        <textarea
          className="w-full rounded border px-3 py-2 text-sm"
          rows={3}
          value={beschreibung}
          onChange={(e) => setBeschreibung(e.target.value)}
        />
      </div>
      {!anwendbar && (
        <div>
          <label className="mb-1 block text-sm">
            Begründung für SoA-Ausschluss (Pflicht)
          </label>
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            rows={3}
            value={begruendung}
            onChange={(e) => setBegruendung(e.target.value)}
            required={!anwendbar}
          />
        </div>
      )}
      <div className="flex justify-end gap-2 pt-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Abbrechen
        </Button>
        <Button type="submit" disabled={isPending}>
          Speichern
        </Button>
      </div>
    </form>
  );
}
