/**
 * Liste der 93 Annex-A-Controls mit Filter nach Kategorie + Status.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { type ImplementationStatus, listControls } from "@/lib/api/iso27001";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Link } from "react-router-dom";

const STATUS_LABEL: Record<ImplementationStatus, string> = {
  verifiziert: "Verifiziert",
  umgesetzt: "Umgesetzt",
  geplant: "Geplant",
  nicht_bewertet: "Nicht bewertet",
  nicht_anwendbar: "Nicht anwendbar",
};

const STATUS_BG: Record<ImplementationStatus, string> = {
  verifiziert: "bg-emerald-100 text-emerald-800",
  umgesetzt: "bg-blue-100 text-blue-800",
  geplant: "bg-amber-100 text-amber-800",
  nicht_bewertet: "bg-slate-100 text-slate-600",
  nicht_anwendbar: "bg-white border text-slate-500",
};

const KATEGORIE_LABEL = {
  A5: "A.5 Organisatorisch",
  A6: "A.6 Personell",
  A7: "A.7 Physisch",
  A8: "A.8 Technologisch",
};

export function Iso27001ControlList() {
  const [kategorieFilter, setKategorieFilter] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["iso27001-controls", kategorieFilter],
    queryFn: () => listControls({ kategorie: kategorieFilter || undefined }),
  });

  const filtered = data?.results.filter(
    (c) => !statusFilter || c.status === statusFilter,
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle>ISO 27001 Annex-A-Controls (93)</CardTitle>
        <div className="mt-3 flex flex-wrap gap-2">
          <select
            className="border rounded px-2 py-1 text-sm"
            value={kategorieFilter}
            onChange={(e) => setKategorieFilter(e.target.value)}
          >
            <option value="">Alle Kategorien</option>
            {Object.entries(KATEGORIE_LABEL).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
          <select
            className="border rounded px-2 py-1 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="">Alle Status</option>
            {Object.entries(STATUS_LABEL).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </div>
      </CardHeader>
      <CardContent>
        {isError ? (
          <p className="text-destructive">
            Controls konnten nicht geladen werden — bitte Seite neu laden.
          </p>
        ) : isLoading ? (
          <p>Lade Controls …</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-20">Code</TableHead>
                <TableHead>Name</TableHead>
                <TableHead className="w-32">Kategorie</TableHead>
                <TableHead className="w-32">Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filtered?.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono text-xs">{c.code}</TableCell>
                  <TableCell>
                    <Link
                      to={`/iso27001/controls/${c.code}`}
                      className="hover:underline"
                    >
                      {c.name}
                    </Link>
                  </TableCell>
                  <TableCell className="text-xs">
                    {KATEGORIE_LABEL[c.kategorie]}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`inline-block rounded px-2 py-0.5 text-xs ${STATUS_BG[c.status]}`}
                    >
                      {STATUS_LABEL[c.status]}
                    </span>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
