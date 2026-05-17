/**
 * Audits + Findings.
 *
 * TODO(phase3-cleanup): Audit-Create-Form, Finding-Inline-Edit, Maßnahmen-Tracking.
 */

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { listAudits, listFindings } from "@/lib/api/iso27001";
import { useQuery } from "@tanstack/react-query";

export function Iso27001Audits() {
  const { data: audits } = useQuery({
    queryKey: ["iso27001-audits"],
    queryFn: listAudits,
  });
  const { data: findings } = useQuery({
    queryKey: ["iso27001-findings"],
    queryFn: listFindings,
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Internes Audit-Programm (ISO 9.2)</CardTitle>
        </CardHeader>
        <CardContent>
          {!audits || audits.results.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Noch kein Audit geplant. TODO(phase3-cleanup): Anlege-Form.
            </p>
          ) : (
            <ul className="space-y-2">
              {audits.results.map((a) => (
                <li key={a.id} className="border rounded p-2 text-sm">
                  <div className="font-medium">{a.titel}</div>
                  <div className="text-xs text-muted-foreground">
                    {a.auditzeitraum_von} bis {a.auditzeitraum_bis} · {a.auditor} · {a.status} ·{" "}
                    {a.findings_count} Findings
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Findings</CardTitle>
        </CardHeader>
        <CardContent>
          {!findings || findings.results.length === 0 ? (
            <p className="text-sm text-muted-foreground">Keine Findings erfasst.</p>
          ) : (
            <ul className="space-y-2">
              {findings.results.map((f) => (
                <li key={f.id} className="border rounded p-2 text-sm">
                  <div className="font-medium">
                    [{f.schweregrad}] {f.beschreibung.slice(0, 100)}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {f.massnahme} · geplant bis {f.geplant_bis ?? "—"}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
