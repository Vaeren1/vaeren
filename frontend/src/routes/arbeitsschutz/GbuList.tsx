/**
 * GBU-Übersicht: alle Gefährdungsbeurteilungen mit Status-Ampel.
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
import { listGbu, type GbuStatus } from "@/lib/api/arbeitsschutz";
import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";

const STATUS_BADGE: Record<GbuStatus, string> = {
  entwurf: "text-slate-700",
  in_bewertung: "text-amber-700",
  freigegeben: "text-emerald-700 font-semibold",
  zu_ueberarbeiten: "text-rose-700",
};

const STATUS_LABEL: Record<GbuStatus, string> = {
  entwurf: "Entwurf",
  in_bewertung: "In Bewertung",
  freigegeben: "Freigegeben",
  zu_ueberarbeiten: "Zu überarbeiten",
};

export function GbuListPage() {
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({ queryKey: ["as-gbu"], queryFn: listGbu });
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Gefährdungsbeurteilungen</CardTitle>
            <p className="text-sm text-muted-foreground">
              ArbSchG §5. Eine GBU pro Tätigkeit, Wirksamkeitsprüfung jährlich.
            </p>
          </div>
          <Button onClick={() => navigate("/arbeitsschutz/gbu/neu")}>
            + Neue GBU
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade…</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Noch keine GBU angelegt.
          </p>
        )}
        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Bereich · Tätigkeit</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Wirksamk.-Prüfung</TableHead>
                <TableHead>Aktuell?</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((g) => (
                <TableRow key={g.id}>
                  <TableCell>
                    <Link to={`/arbeitsschutz/gbu/${g.id}`} className="underline">
                      {g.titel}
                    </Link>
                  </TableCell>
                  <TableCell className="text-xs">
                    {g.arbeitsbereich_name} · {g.taetigkeit_name}
                  </TableCell>
                  <TableCell className={STATUS_BADGE[g.status]}>
                    {STATUS_LABEL[g.status]}
                  </TableCell>
                  <TableCell className="text-xs">
                    {g.wirksamkeitspruefung_faellig_am}
                    {g.ist_ueberfaellig && (
                      <span className="ml-2 text-rose-700">überfällig</span>
                    )}
                  </TableCell>
                  <TableCell>{g.ist_aktuell ? "✓" : "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
