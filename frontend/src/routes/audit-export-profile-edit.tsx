/**
 * Bearbeiten eines bestehenden AuditExportProfile.
 *
 * Route: /audit-export/profil/:id
 * Lädt das Profile per GET, speichert via PATCH /api/audit-export/profiles/:id/.
 */

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  ALL_NORMS,
  ALL_TEMPLATES,
} from "@/lib/api/audit_export_constants";
import {
  getProfile,
  NORM_LABEL,
  TEMPLATE_LABEL,
  updateProfile,
  type AuditExportProfile,
  type AuditTemplate,
  type EvidenceMode,
  type NormScope,
} from "@/lib/api/audit_export";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";

export function AuditExportProfileEditPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number.parseInt(id, 10) : NaN;
  const navigate = useNavigate();
  const qc = useQueryClient();

  const profileQuery = useQuery({
    queryKey: ["audit-export", "profile", numericId],
    queryFn: () => getProfile(numericId),
    enabled: !Number.isNaN(numericId),
  });

  const [name, setName] = useState("");
  const [template, setTemplate] = useState<AuditTemplate>("iso_27001_audit");
  const [normScope, setNormScope] = useState<NormScope[]>([]);
  const [zeitraumVon, setZeitraumVon] = useState("");
  const [zeitraumBis, setZeitraumBis] = useState("");
  const [evidenceMode, setEvidenceMode] = useState<EvidenceMode>("embed");
  const [anonymisierenPii, setAnonymisierenPii] = useState(false);
  const [watermarkDraft, setWatermarkDraft] = useState(false);

  useEffect(() => {
    const p = profileQuery.data;
    if (!p) return;
    setName(p.name);
    setTemplate(p.template);
    setNormScope(p.norm_scope);
    setZeitraumVon(p.zeitraum_von);
    setZeitraumBis(p.zeitraum_bis);
    setEvidenceMode(p.evidence_mode);
    setAnonymisierenPii(p.anonymisieren_pii);
    setWatermarkDraft(p.watermark_draft);
  }, [profileQuery.data]);

  const mut = useMutation({
    mutationFn: (payload: Partial<AuditExportProfile>) =>
      updateProfile(numericId, payload),
    onSuccess: () => {
      toast.success("Profile gespeichert.");
      qc.invalidateQueries({ queryKey: ["audit-export", "profiles"] });
      qc.invalidateQueries({ queryKey: ["audit-export", "profile", numericId] });
      navigate("/audit-export");
    },
    onError: (e: unknown) => {
      const msg = e instanceof Error ? e.message : String(e);
      toast.error(`Speichern fehlgeschlagen: ${msg}`);
    },
  });

  const toggleNorm = (norm: NormScope) =>
    setNormScope((prev) =>
      prev.includes(norm) ? prev.filter((n) => n !== norm) : [...prev, norm],
    );

  if (profileQuery.isLoading) {
    return <p>Lade Profile …</p>;
  }
  if (profileQuery.isError || !profileQuery.data) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-destructive">
            Profile nicht gefunden oder Ladefehler.
          </p>
          <Button
            variant="outline"
            className="mt-3"
            onClick={() => navigate("/audit-export")}
          >
            Zurück zur Übersicht
          </Button>
        </CardContent>
      </Card>
    );
  }

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mut.mutate({
      name: name.trim(),
      template,
      norm_scope: normScope,
      zeitraum_von: zeitraumVon,
      zeitraum_bis: zeitraumBis,
      evidence_mode: evidenceMode,
      anonymisieren_pii: anonymisierenPii,
      watermark_draft: watermarkDraft,
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Profile bearbeiten</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Änderungen wirken auf zukünftige Runs. Bestehende Runs bleiben unverändert.
        </p>
      </CardHeader>
      <form onSubmit={onSubmit}>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="name">Profile-Name</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="from">Zeitraum von</Label>
              <Input
                id="from"
                type="date"
                value={zeitraumVon}
                onChange={(e) => setZeitraumVon(e.target.value)}
                required
              />
            </div>
            <div>
              <Label htmlFor="to">Zeitraum bis</Label>
              <Input
                id="to"
                type="date"
                value={zeitraumBis}
                onChange={(e) => setZeitraumBis(e.target.value)}
                required
              />
            </div>
          </div>

          <div>
            <Label>Norm-Scope</Label>
            <div className="grid grid-cols-2 gap-2 mt-1">
              {ALL_NORMS.map((n) => (
                <label key={n} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={normScope.includes(n)}
                    onChange={() => toggleNorm(n)}
                  />
                  {NORM_LABEL[n]}
                </label>
              ))}
            </div>
          </div>

          <div>
            <Label htmlFor="template">Audit-Template</Label>
            <select
              id="template"
              className="block w-full rounded border border-input bg-background p-2 text-sm"
              value={template}
              onChange={(e) => setTemplate(e.target.value as AuditTemplate)}
            >
              {ALL_TEMPLATES.map((t) => (
                <option key={t} value={t}>
                  {TEMPLATE_LABEL[t]}
                </option>
              ))}
            </select>
          </div>

          <div>
            <Label>Belege im Bundle</Label>
            <div className="space-y-1 mt-1">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name="evidence-mode"
                  checked={evidenceMode === "embed"}
                  onChange={() => setEvidenceMode("embed")}
                />
                Original-Dateien einbetten
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="radio"
                  name="evidence-mode"
                  checked={evidenceMode === "reference"}
                  onChange={() => setEvidenceMode("reference")}
                />
                Nur Hash-Referenzen
              </label>
            </div>
          </div>

          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={anonymisierenPii}
              onChange={(e) => setAnonymisierenPii(e.target.checked)}
            />
            Mitarbeiter-Namen anonymisieren (MA-001, MA-002, …)
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={watermarkDraft}
              onChange={(e) => setWatermarkDraft(e.target.checked)}
            />
            DRAFT-Wasserzeichen ins PDF einfügen
          </label>
        </CardContent>
        <CardFooter className="flex justify-between border-t pt-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/audit-export")}
          >
            Abbrechen
          </Button>
          <Button type="submit" disabled={mut.isPending}>
            {mut.isPending ? "Speichere …" : "Speichern"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
