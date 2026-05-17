/**
 * Control-Detail mit Implementation-Editor + LLM-Entwurfshilfe + Evidence-Links.
 *
 * Drei Spalten:
 * 1. Stammdaten (links)
 * 2. Implementation-Editor mit "LLM-Entwurf"-Button + Verify-Aktion
 * 3. Evidence-Links (rechts) — bestätigt + Vorschläge
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  confirmEvidenceLink,
  getControl,
  getImplementation,
  llmEntwurfImplementation,
  updateImplementation,
  verifyImplementation,
  type ImplementationStatus,
} from "@/lib/api/iso27001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";

export function Iso27001ControlDetail() {
  const { code } = useParams<{ code: string }>();
  const qc = useQueryClient();
  const [beschreibung, setBeschreibung] = useState("");
  const [status, setStatus] = useState<ImplementationStatus>("nicht_bewertet");

  const { data: control } = useQuery({
    queryKey: ["iso27001-control", code],
    queryFn: () => getControl(code!),
    enabled: !!code,
  });

  const { data: impl, refetch } = useQuery({
    queryKey: ["iso27001-impl", control?.implementation_id],
    queryFn: () => getImplementation(control!.implementation_id!),
    enabled: !!control?.implementation_id,
  });

  useEffect(() => {
    if (impl) {
      setBeschreibung(impl.implementation_beschreibung);
      setStatus(impl.status);
    }
  }, [impl]);

  const saveMut = useMutation({
    mutationFn: () =>
      updateImplementation(impl!.id, {
        implementation_beschreibung: beschreibung,
        status,
      }),
    onSuccess: () => {
      toast.success("Implementation gespeichert.");
      qc.invalidateQueries({ queryKey: ["iso27001-impl"] });
      qc.invalidateQueries({ queryKey: ["iso27001-controls"] });
    },
  });

  const llmMut = useMutation({
    mutationFn: () => llmEntwurfImplementation(impl!.id),
    onSuccess: () => {
      toast.success("LLM-Entwurf erzeugt. Bitte prüfen + ggf. übernehmen.");
      refetch();
    },
  });

  const verifyMut = useMutation({
    mutationFn: () => verifyImplementation(impl!.id),
    onSuccess: () => {
      toast.success("Control verifiziert.");
      refetch();
      qc.invalidateQueries({ queryKey: ["iso27001-controls"] });
    },
    onError: (err: Error) => {
      toast.error(`Verify fehlgeschlagen: ${err.message}`);
    },
  });

  const confirmEvidenceMut = useMutation({
    mutationFn: (linkId: number) => confirmEvidenceLink(linkId),
    onSuccess: () => {
      toast.success("Evidence bestätigt.");
      refetch();
    },
  });

  if (!control || !impl) {
    return <p>Lade Control …</p>;
  }

  return (
    <div className="space-y-4">
      <div>
        <Link to="/iso27001/controls" className="text-sm text-muted-foreground">
          ← Alle Controls
        </Link>
        <h1 className="text-xl font-semibold mt-1">
          {control.code} {control.name}
        </h1>
        <p className="text-sm text-muted-foreground">
          ISO-Klausel {control.iso_clause} · Kategorie {control.kategorie}
        </p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Stammdaten</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed">{control.description_de}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Implementation</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <Label htmlFor="status">Status</Label>
              <select
                id="status"
                className="w-full border rounded px-2 py-1 text-sm"
                value={status}
                onChange={(e) => setStatus(e.target.value as ImplementationStatus)}
              >
                <option value="nicht_bewertet">Nicht bewertet</option>
                <option value="nicht_anwendbar">Nicht anwendbar</option>
                <option value="geplant">Geplant</option>
                <option value="umgesetzt">Umgesetzt</option>
                <option value="verifiziert" disabled>
                  Verifiziert (über Verify-Aktion)
                </option>
              </select>
            </div>

            <div>
              <Label htmlFor="beschreibung">Beschreibung</Label>
              <Textarea
                id="beschreibung"
                rows={8}
                value={beschreibung}
                onChange={(e) => setBeschreibung(e.target.value)}
              />
            </div>

            {impl.implementation_vorschlag && (
              <div className="rounded border-2 border-amber-400 bg-amber-50 p-3 text-sm">
                <div className="text-xs font-medium text-amber-900 mb-1">
                  LLM-Entwurf — bitte prüfen, KEIN juristischer Rat:
                </div>
                <p className="whitespace-pre-wrap">{impl.implementation_vorschlag}</p>
                <Button
                  size="sm"
                  variant="outline"
                  className="mt-2"
                  onClick={() => setBeschreibung(impl.implementation_vorschlag)}
                >
                  In Beschreibung übernehmen
                </Button>
              </div>
            )}

            <div className="flex flex-wrap gap-2">
              <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>
                Speichern
              </Button>
              <Button
                variant="outline"
                onClick={() => llmMut.mutate()}
                disabled={llmMut.isPending}
              >
                LLM-Entwurf erzeugen
              </Button>
              {status === "umgesetzt" && (
                <Button
                  variant="default"
                  onClick={() => verifyMut.mutate()}
                  disabled={verifyMut.isPending}
                >
                  Verifizieren (HITL-Gate)
                </Button>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Evidence-Verlinkungen</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {impl.evidence_links.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Noch keine Evidence verknüpft.
              </p>
            ) : (
              <>
                <div className="space-y-1">
                  <div className="text-xs font-medium text-muted-foreground">
                    Bestätigt
                  </div>
                  {impl.evidence_links
                    .filter((l) => !l.auto_suggested && l.confirmed_by)
                    .map((l) => (
                      <div
                        key={l.id}
                        className="text-sm border rounded p-2 bg-emerald-50"
                      >
                        {l.evidence_titel}
                        <span className="ml-2 text-xs text-muted-foreground">
                          ({l.quell_modul})
                        </span>
                      </div>
                    ))}
                </div>

                <div className="space-y-1">
                  <div className="text-xs font-medium text-amber-700">
                    Vorschläge — bitte prüfen
                  </div>
                  {impl.evidence_links
                    .filter((l) => l.auto_suggested && !l.confirmed_by)
                    .map((l) => (
                      <div
                        key={l.id}
                        className="text-sm border rounded p-2 bg-amber-50 flex items-center justify-between"
                      >
                        <span>
                          {l.evidence_titel}
                          <span className="ml-2 text-xs text-muted-foreground">
                            ({l.quell_modul})
                          </span>
                        </span>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => confirmEvidenceMut.mutate(l.id)}
                          disabled={confirmEvidenceMut.isPending}
                        >
                          Bestätigen
                        </Button>
                      </div>
                    ))}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
