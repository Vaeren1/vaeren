/**
 * KI-Policies — Liste mit Versionen + Templates + Ratify/New-Version.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  GELTUNGSBEREICH_LABELS,
  createPolicyFromTemplate,
  listPolicies,
  listPolicyTemplates,
  policyKenntnisnahme,
  policyNewVersion,
  policyRatify,
  updatePolicy,
  type AiPolicy,
} from "@/lib/api/iso42001";
import { useMitarbeiterList } from "@/lib/api/mitarbeiter";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

export function Iso42001PoliciesPage() {
  const qc = useQueryClient();
  const { data: policies } = useQuery({
    queryKey: ["iso42001-policies"],
    queryFn: listPolicies,
  });
  const { data: templates } = useQuery({
    queryKey: ["iso42001-policy-templates"],
    queryFn: listPolicyTemplates,
  });
  const [selected, setSelected] = useState<AiPolicy | null>(null);
  const [kenntnisnahmePolicy, setKenntnisnahmePolicy] = useState<AiPolicy | null>(
    null,
  );

  const createFromTemplate = useMutation({
    mutationFn: createPolicyFromTemplate,
    onSuccess: (p) => {
      qc.invalidateQueries({ queryKey: ["iso42001-policies"] });
      toast.success(`Policy "${p.titel}" aus Template angelegt (Entwurf).`);
      setSelected(p);
    },
  });

  const ratifyMut = useMutation({
    mutationFn: (id: number) => policyRatify(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-policies"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("Policy ratifiziert + aktiv geschaltet.");
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Fehler beim Ratifizieren";
      toast.error(msg);
    },
  });

  const newVersionMut = useMutation({
    mutationFn: (vars: { id: number; payload: { titel?: string; inhalt_markdown?: string } }) =>
      policyNewVersion(vars.id, vars.payload),
    onSuccess: (p) => {
      qc.invalidateQueries({ queryKey: ["iso42001-policies"] });
      toast.success(`Neue Version v${p.version} angelegt.`);
      setSelected(p);
    },
  });

  const kenntnisnahmeMut = useMutation({
    mutationFn: (vars: { policyId: number; mitarbeiter_id: number }) =>
      policyKenntnisnahme(vars.policyId, vars.mitarbeiter_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-policies"] });
      toast.success("Kenntnisnahme erfasst.");
      setKenntnisnahmePolicy(null);
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : "Fehler bei Kenntnisnahme";
      toast.error(msg);
    },
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">KI-Policies</h1>
        <p className="text-sm text-muted-foreground">
          Versionierte Richtlinien für den verantwortungsvollen KI-Einsatz. Aktivierung
          (Ratifizierung) durch die Geschäftsführung.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Aus Template anlegen</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          {templates?.map((t) => (
            <Button
              key={t.slug}
              variant="outline"
              size="sm"
              onClick={() => createFromTemplate.mutate(t.slug)}
              disabled={createFromTemplate.isPending}
            >
              + {t.titel}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Policies</CardTitle>
        </CardHeader>
        <CardContent>
          {policies && policies.results.length === 0 && (
            <p className="text-sm text-muted-foreground">
              Noch keine Policies angelegt. Starte mit einem Template oben.
            </p>
          )}
          <ul className="divide-y">
            {policies?.results.map((p) => (
              <li key={p.id} className="flex items-center justify-between gap-3 py-2">
                <button
                  type="button"
                  className="text-left"
                  onClick={() => setSelected(p)}
                >
                  <div className="font-medium">
                    {p.titel} <span className="text-xs text-slate-500">v{p.version}</span>
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {GELTUNGSBEREICH_LABELS[p.geltungsbereich]} ·{" "}
                    {p.aktiv ? (
                      <span className="text-emerald-700 font-medium">aktiv</span>
                    ) : (
                      <span>inaktiv</span>
                    )}{" "}
                    · {p.kenntnisnahmen_count} Kenntnisnahmen
                  </div>
                </button>
                <div className="flex gap-2">
                  {!p.aktiv && (
                    <Button
                      size="sm"
                      onClick={() => ratifyMut.mutate(p.id)}
                      disabled={ratifyMut.isPending}
                    >
                      Ratifizieren
                    </Button>
                  )}
                  {p.aktiv && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setKenntnisnahmePolicy(p)}
                    >
                      Kenntnisnahme abgeben
                    </Button>
                  )}
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      newVersionMut.mutate({
                        id: p.id,
                        payload: { inhalt_markdown: p.inhalt_markdown },
                      })
                    }
                  >
                    Neue Version
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      {selected && (
        <PolicyEditor
          policy={selected}
          onClose={() => setSelected(null)}
          onSaved={() => {
            qc.invalidateQueries({ queryKey: ["iso42001-policies"] });
          }}
        />
      )}

      {kenntnisnahmePolicy && (
        <KenntnisnahmeDialog
          policy={kenntnisnahmePolicy}
          onCancel={() => setKenntnisnahmePolicy(null)}
          onConfirm={(mitarbeiter_id) =>
            kenntnisnahmeMut.mutate({
              policyId: kenntnisnahmePolicy.id,
              mitarbeiter_id,
            })
          }
          isPending={kenntnisnahmeMut.isPending}
        />
      )}
    </div>
  );
}

function KenntnisnahmeDialog({
  policy,
  onCancel,
  onConfirm,
  isPending,
}: {
  policy: AiPolicy;
  onCancel: () => void;
  onConfirm: (mitarbeiter_id: number) => void;
  isPending: boolean;
}) {
  const mitarbeiter = useMitarbeiterList();
  const [selectedId, setSelectedId] = useState<number | "">("");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[480px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          if (selectedId !== "") onConfirm(Number(selectedId));
        }}
      >
        <h2 className="mb-2 text-lg font-semibold">Kenntnisnahme abgeben</h2>
        <p className="text-sm text-muted-foreground">
          Bestätigt, dass der/die gewählte Mitarbeiter:in die Policy{" "}
          <strong>{policy.titel}</strong> v{policy.version} gelesen und verstanden
          hat.
        </p>
        <div className="mt-3">
          <label className="text-sm font-medium">Mitarbeiter:in</label>
          <select
            className="mt-1 w-full rounded border px-3 py-2 text-sm"
            value={selectedId}
            onChange={(e) =>
              setSelectedId(e.target.value ? Number(e.target.value) : "")
            }
            required
          >
            <option value="">— Bitte wählen —</option>
            {mitarbeiter.data?.results.map((m) => (
              <option key={m.id} value={m.id}>
                {m.nachname}, {m.vorname} ({m.abteilung})
              </option>
            ))}
          </select>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending || selectedId === ""}>
            Bestätigen
          </Button>
        </div>
      </form>
    </div>
  );
}

function PolicyEditor({
  policy,
  onClose,
  onSaved,
}: {
  policy: AiPolicy;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [titel, setTitel] = useState(policy.titel);
  const [inhalt, setInhalt] = useState(policy.inhalt_markdown);
  const saveMut = useMutation({
    mutationFn: () => updatePolicy(policy.id, { titel, inhalt_markdown: inhalt }),
    onSuccess: () => {
      toast.success("Policy gespeichert.");
      onSaved();
      onClose();
    },
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <div className="w-[800px] max-w-full rounded-md bg-white p-6 shadow-xl">
        <h2 className="mb-3 text-lg font-semibold">
          Policy bearbeiten — {policy.titel} v{policy.version}
        </h2>
        <div className="space-y-3">
          <input
            className="w-full rounded border px-3 py-2"
            value={titel}
            onChange={(e) => setTitel(e.target.value)}
            disabled={policy.aktiv}
          />
          <textarea
            className="w-full rounded border px-3 py-2 font-mono text-sm"
            rows={20}
            value={inhalt}
            onChange={(e) => setInhalt(e.target.value)}
            disabled={policy.aktiv}
          />
          {policy.aktiv && (
            <p className="text-xs text-amber-700">
              Aktive Policies sind read-only — lege eine neue Version an, um Änderungen zu erfassen.
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={onClose}>
              Schließen
            </Button>
            {!policy.aktiv && (
              <Button onClick={() => saveMut.mutate()} disabled={saveMut.isPending}>
                Speichern
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
