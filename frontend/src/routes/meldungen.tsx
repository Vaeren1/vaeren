/**
 * Internes Bearbeiter-Dashboard: Liste aller HinSchG-Meldungen.
 * Permission: GF (lesen) + Compliance-Beauftragter (lesen+bearbeiten).
 */

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useMeldungList } from "@/lib/api/hinschg";
import { Link } from "react-router-dom";

export function MeldungenListPage() {
  const { data, isLoading, isError } = useMeldungList();

  // Public-Form + Status-Abfrage liegen auf eigener Subdomain in Production
  // (hinweise.app.vaeren.de). Lokal/Dev: gleicher Origin.
  const publicOrigin =
    typeof window !== "undefined" && window.location.host.startsWith("app.")
      ? `${window.location.protocol}//hinweise.${window.location.host.slice(4)}`
      : "";
  const publicFormUrl = `${publicOrigin}/hinweise`;

  return (
    <div className="space-y-4">
      <Card className="border-emerald-200 bg-emerald-50/50">
        <CardHeader>
          <CardTitle className="text-base">
            Hinweisgeber-Portal (öffentlich)
          </CardTitle>
          <CardDescription>
            Diese URLs gibst du an Mitarbeitende + Lieferanten weiter. Beide
            sind ohne Login zugänglich.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex items-baseline gap-2">
            <span className="text-muted-foreground">Meldung einreichen:</span>
            <a
              href={publicFormUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono underline"
            >
              {publicFormUrl}
            </a>
          </div>
          <div className="text-xs text-muted-foreground">
            Hinweisgeber:innen erhalten nach Submit ein Token + persönliche
            Status-Seite. Den Link zur Status-Seite findest du je Meldung in der
            Tabelle unten.
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>HinSchG-Meldungen</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Lade …</p>}
          {isError && (
            <p className="text-destructive">
              Keine Berechtigung oder Fehler beim Laden.
            </p>
          )}
          {data && data.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Bisher keine Meldungen eingegangen.
            </p>
          )}
          {data && data.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Eingegangen</TableHead>
                  <TableHead>Titel</TableHead>
                  <TableHead>Anonym</TableHead>
                  <TableHead>Kategorie</TableHead>
                  <TableHead>Schweregrad</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Frist (3M)</TableHead>
                  <TableHead>Hinweisgeber-Sicht</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((m) => {
                  const statusUrl = `${publicOrigin}/hinweise/status/${m.eingangs_token}`;
                  return (
                    <TableRow key={m.id}>
                      <TableCell>
                        {new Date(m.eingegangen_am).toLocaleDateString("de-DE")}
                      </TableCell>
                      <TableCell>
                        <Link
                          to={`/meldungen/${m.id}`}
                          className="font-medium underline"
                        >
                          {m.titel}
                        </Link>
                      </TableCell>
                      <TableCell>{m.anonym ? "ja" : "nein"}</TableCell>
                      <TableCell>{m.kategorie || "—"}</TableCell>
                      <TableCell>{m.schweregrad || "—"}</TableCell>
                      <TableCell>{m.status_display}</TableCell>
                      <TableCell>{m.rueckmeldung_faellig_bis}</TableCell>
                      <TableCell>
                        <a
                          href={statusUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs underline"
                          title="Was Hinweisgeber:in zu dieser Meldung sieht (anonym, Token-gestützt)"
                        >
                          Status ↗
                        </a>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
