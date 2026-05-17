/**
 * SoA-Generator: zeigt vorhandene Versionen + Button "Neue Version erzeugen".
 *
 * TODO(phase3-cleanup): Wizard mit Geltungsbereich-Editor + Download-Button für PDF.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { erzeugeSoa, listSoa } from "@/lib/api/iso27001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

export function Iso27001SoaGenerator() {
  const qc = useQueryClient();
  const [version, setVersion] = useState("");
  const [geltungsbereich, setGeltungsbereich] = useState("");

  const { data } = useQuery({
    queryKey: ["iso27001-soa"],
    queryFn: listSoa,
  });

  const createMut = useMutation({
    mutationFn: () => erzeugeSoa({ version, geltungsbereich }),
    onSuccess: () => {
      toast.success("SoA-Version erzeugt.");
      qc.invalidateQueries({ queryKey: ["iso27001-soa"] });
      setVersion("");
      setGeltungsbereich("");
    },
  });

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>SoA — Neue Version erzeugen</CardTitle>
          <p className="text-sm text-muted-foreground mt-1">
            Snapshottet alle 93 Controls mit Implementation + Evidence-Anzahl.
          </p>
        </CardHeader>
        <CardContent className="space-y-3">
          <div>
            <label htmlFor="soa-version" className="text-sm">
              Version
            </label>
            <input
              id="soa-version"
              type="text"
              className="w-full border rounded px-2 py-1"
              placeholder="1.0"
              value={version}
              onChange={(e) => setVersion(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="geltungsbereich" className="text-sm">
              Geltungsbereich (Scope-Statement)
            </label>
            <textarea
              id="geltungsbereich"
              className="w-full border rounded px-2 py-1"
              rows={3}
              value={geltungsbereich}
              onChange={(e) => setGeltungsbereich(e.target.value)}
            />
          </div>
          <Button
            onClick={() => createMut.mutate()}
            disabled={!version || createMut.isPending}
          >
            SoA-Version anlegen
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Vorhandene Versionen</CardTitle>
        </CardHeader>
        <CardContent>
          {!data || data.results.length === 0 ? (
            <p className="text-sm text-muted-foreground">Noch keine Version erzeugt.</p>
          ) : (
            <ul className="space-y-2">
              {data.results.map((s) => (
                <li key={s.id} className="flex items-center justify-between border-b pb-1 text-sm">
                  <span>v{s.version} — {new Date(s.erstellt_am).toLocaleDateString("de-DE")}</span>
                  <a
                    href={`/api/iso27001/soa/${s.id}/pdf/`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-blue-600 underline"
                  >
                    PDF
                  </a>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
