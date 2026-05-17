/**
 * KI-Tool-Inventar (EU AI Act).
 *
 * Auflistung der eingesetzten KI-Tools mit Risikoklasse + Pflicht-Indikator.
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
import { listKITools, type KIRisikoKlasse } from "@/lib/api/ki_inventar";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";

const RISIKO_FARBE: Record<KIRisikoKlasse, string> = {
  unakzeptabel: "text-red-700 font-semibold",
  hoch: "text-red-700",
  begrenzt: "text-amber-700",
  minimal: "text-emerald-700",
  unbekannt: "text-muted-foreground",
};

const RISIKO_LABEL: Record<KIRisikoKlasse, string> = {
  unakzeptabel: "Unakzeptabel (verboten)",
  hoch: "Hochrisiko",
  begrenzt: "Begrenzt",
  minimal: "Minimal",
  unbekannt: "noch unbekannt",
};

export function KIInventarListPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["ki-tools"],
    queryFn: listKITools,
  });
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle>KI-Tool-Inventar</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            EU AI Act Art. 26: Betreiber von Hochrisiko-KI-Systemen führen ein Verzeichnis.
          </p>
        </div>
        <Button asChild>
          <Link to="/ki-inventar/neu">+ KI-Tool erfassen</Link>
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading && <p>Lade …</p>}
        {data && data.results.length === 0 && (
          <p className="text-muted-foreground">
            Noch keine KI-Tools erfasst.{" "}
            <Link to="/ki-inventar/neu" className="underline">
              Erstes Tool anlegen
            </Link>{" "}
            (auch ChatGPT, Copilot, DeepL etc. zählen).
          </p>
        )}
        {data && data.results.length > 0 && (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name / Anbieter</TableHead>
                <TableHead>Risiko (AI Act)</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Daten</TableHead>
                <TableHead>Aufsicht?</TableHead>
                <TableHead>Transparenz?</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((k) => (
                <TableRow key={k.id}>
                  <TableCell>
                    <Link to={`/ki-inventar/${k.id}`} className="underline">
                      <strong>{k.name}</strong>
                    </Link>
                    <p className="text-xs text-muted-foreground">{k.anbieter}</p>
                  </TableCell>
                  <TableCell className={RISIKO_FARBE[k.risiko] ?? ""}>
                    {RISIKO_LABEL[k.risiko] ?? k.risiko}
                  </TableCell>
                  <TableCell>{k.status}</TableCell>
                  <TableCell className="text-xs">{k.datenkategorie_sensibilitaet}</TableCell>
                  <TableCell>{k.menschliche_aufsicht ? "✓" : "—"}</TableCell>
                  <TableCell>{k.transparenz_information ? "✓" : "—"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
