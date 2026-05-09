/**
 * Public Status-Page (Token-basiert). Zeigt sanitized Status + erlaubt
 * Hinweisgeber-Nachricht-Versand.
 */

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { sendHinweisgeberNachricht, useMeldungStatus } from "@/lib/api/hinschg";
import { useState } from "react";
import { useParams } from "react-router-dom";

const STATUS_LABEL: Record<string, string> = {
  eingegangen: "Eingegangen",
  bestaetigt: "Eingangsbestätigung versandt",
  in_pruefung: "In Prüfung",
  massnahme: "Maßnahme eingeleitet",
  abgeschlossen: "Abgeschlossen",
  abgewiesen: "Abgewiesen",
};

export function PublicHinweiseStatusPage() {
  const { token } = useParams<{ token: string }>();
  const { data, isLoading, isError, refetch } = useMeldungStatus(token);
  const [nachricht, setNachricht] = useState("");
  const [sending, setSending] = useState(false);
  const [sendOk, setSendOk] = useState(false);

  async function handleSend(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    setSending(true);
    setSendOk(false);
    try {
      await sendHinweisgeberNachricht(token, nachricht);
      setNachricht("");
      setSendOk(true);
      refetch();
    } catch {
      setSendOk(false);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="container mx-auto max-w-2xl py-12 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Status Ihrer Meldung</CardTitle>
          <CardDescription>
            Token: <span className="break-all font-mono text-xs">{token}</span>
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading && <p>Lade …</p>}
          {isError && (
            <p className="text-destructive">Token unbekannt oder ungültig.</p>
          )}
          {data && (
            <dl className="space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Status:</dt>
                <dd className="font-medium">
                  {STATUS_LABEL[data.status] ?? data.status}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Eingegangen am:</dt>
                <dd>{new Date(data.eingegangen_am).toLocaleString("de-DE")}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Eingangsbestätigung:</dt>
                <dd>
                  {data.bestaetigung_versandt_am
                    ? new Date(data.bestaetigung_versandt_am).toLocaleString(
                        "de-DE",
                      )
                    : "ausstehend"}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-muted-foreground">Rückmeldung bis:</dt>
                <dd>{data.rueckmeldung_faellig_bis}</dd>
              </div>
              {data.abgeschlossen_am && (
                <div className="flex justify-between">
                  <dt className="text-muted-foreground">Abgeschlossen am:</dt>
                  <dd>
                    {new Date(data.abgeschlossen_am).toLocaleString("de-DE")}
                  </dd>
                </div>
              )}
            </dl>
          )}
        </CardContent>
      </Card>

      {data && (
        <Card>
          <CardHeader>
            <CardTitle>Verlauf</CardTitle>
            <CardDescription>
              Aus Vertraulichkeitsgründen werden interne Notizen und Bearbeiter
              nicht angezeigt.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {data.bearbeitungsschritte.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Bisher keine Schritte protokolliert.
              </p>
            ) : (
              <ul className="space-y-2 text-sm">
                {data.bearbeitungsschritte.map((s, i) => (
                  <li
                    key={`${s.timestamp}-${i}`}
                    className="flex justify-between border-b pb-1"
                  >
                    <span>{s.aktion}</span>
                    <span className="text-muted-foreground">
                      {new Date(s.timestamp).toLocaleString("de-DE")}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Nachricht nachreichen</CardTitle>
          <CardDescription>
            Sie können jederzeit weitere Informationen anonym hinzufügen.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSend} className="space-y-3">
            <Textarea
              required
              rows={5}
              value={nachricht}
              onChange={(e) => setNachricht(e.target.value)}
              placeholder="Ergänzende Hinweise, neue Beobachtungen …"
            />
            {sendOk && (
              <p className="text-sm text-green-700">
                Nachricht erfolgreich übermittelt.
              </p>
            )}
            <Button type="submit" disabled={sending}>
              {sending ? "Sende …" : "Nachricht absenden"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
