/**
 * Risiko-Register mit Tabelle + Heatmap.
 *
 * TODO(phase3-cleanup): Inline-Edit-Form, 5x5-Heatmap-Visualisierung,
 * Treatment-Vorschlag-Panel, Akzeptanz-Workflow für GF.
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
import { listRisiken } from "@/lib/api/iso27001";
import { useQuery } from "@tanstack/react-query";

export function Iso27001RiskRegister() {
  const { data, isLoading } = useQuery({
    queryKey: ["iso27001-risiken"],
    queryFn: listRisiken,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>ISMS-Risiko-Register</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Risk-Score = Likelihood × Impact (1–25). Vom Tenant verantwortet.
        </p>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <p>Lade …</p>
        ) : !data || data.results.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            Noch keine Risiken erfasst. TODO(phase3-cleanup): Anlege-Form.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Titel</TableHead>
                <TableHead>Likelihood</TableHead>
                <TableHead>Impact</TableHead>
                <TableHead>Score</TableHead>
                <TableHead>Treatment</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.results.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{r.titel}</TableCell>
                  <TableCell>{r.likelihood}</TableCell>
                  <TableCell>{r.impact}</TableCell>
                  <TableCell className="font-mono">{r.risk_score_brutto}</TableCell>
                  <TableCell>{r.treatment}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
