/**
 * Management-Review-Liste (Jahres-Reviews nach ISO 9.3).
 *
 * TODO(phase3-cleanup): Detail-View mit Inputs/Outputs-Editor, "Inputs vorbefuellen"-
 * Button, PDF-Export. GF-only-Genehmigung.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listMgtReviews } from "@/lib/api/iso27001";
import { useQuery } from "@tanstack/react-query";

export function Iso27001ManagementReview() {
  const { data } = useQuery({
    queryKey: ["iso27001-mgt-reviews"],
    queryFn: listMgtReviews,
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>Management-Review (ISO 9.3)</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Jährlicher Review durch GF. Inputs (Audit-Ergebnisse, Findings, Risiken,
          Performance) werden automatisch aus den letzten 12 Monaten vorbefüllt.
        </p>
      </CardHeader>
      <CardContent>
        {!data || data.results.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            Noch kein Review erstellt. TODO(phase3-cleanup): Anlege-Form.
          </p>
        ) : (
          <ul className="space-y-2">
            {data.results.map((m) => (
              <li key={m.id} className="border rounded p-2 text-sm">
                <div className="font-medium">Review {m.review_jahr}</div>
                <div className="text-xs text-muted-foreground">
                  Status: {m.status} · {m.durchgefuehrt_am ?? "noch nicht durchgeführt"}
                </div>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
