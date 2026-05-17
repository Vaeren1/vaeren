/**
 * 5-Step-Wizard zum Anlegen eines AuditExportProfile.
 *
 * Steps: 1 Name+Zeitraum → 2 Norm-Scope → 3 Template → 4 Optionen → 5 Preview+Generate.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createProfile,
  NORM_LABEL,
  startRun,
  TEMPLATE_LABEL,
  type AuditTemplate,
  type EvidenceMode,
  type NormScope,
} from "@/lib/api/audit_export";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

const ALL_NORMS: NormScope[] = [
  "iso_27001",
  "iso_42001",
  "nis2",
  "dsgvo",
  "ai_act",
  "arbeitsschutz",
  "pflichtunterweisung",
  "hinschg",
  "avv",
  "datenpannen",
  "transparenzregister",
];

const ALL_TEMPLATES: AuditTemplate[] = [
  "iso_27001_audit",
  "gap_analyse",
  "tisax_light",
  "ai_act_konformitaet",
  "nis2_behoerden_vorlage",
  "bfdi_template",
  "geschaeftsfuehrer_mappe",
];

function defaultDateRange(): { from: string; to: string } {
  const today = new Date();
  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(today.getFullYear() - 1);
  return {
    from: oneYearAgo.toISOString().slice(0, 10),
    to: today.toISOString().slice(0, 10),
  };
}

export function AuditExportWizardPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);

  const [name, setName] = useState("");
  const initial = defaultDateRange();
  const [zeitraumVon, setZeitraumVon] = useState(initial.from);
  const [zeitraumBis, setZeitraumBis] = useState(initial.to);
  const [normScope, setNormScope] = useState<NormScope[]>(["iso_27001"]);
  const [template, setTemplate] = useState<AuditTemplate>("iso_27001_audit");
  const [evidenceMode, setEvidenceMode] = useState<EvidenceMode>("embed");
  const [anonymisierenPii, setAnonymisierenPii] = useState(false);
  const [watermarkDraft, setWatermarkDraft] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggleNorm = (norm: NormScope) => {
    setNormScope((prev) =>
      prev.includes(norm) ? prev.filter((n) => n !== norm) : [...prev, norm],
    );
  };

  const canNext = (() => {
    if (step === 1) return name.trim().length > 0 && zeitraumVon && zeitraumBis;
    if (step === 2) return normScope.length > 0;
    return true;
  })();

  const submit = async () => {
    setSubmitting(true);
    setError(null);
    try {
      const profile = await createProfile({
        name: name.trim(),
        template,
        norm_scope: normScope,
        zeitraum_von: zeitraumVon,
        zeitraum_bis: zeitraumBis,
        evidence_mode: evidenceMode,
        anonymisieren_pii: anonymisierenPii,
        watermark_draft: watermarkDraft,
      });
      const run = await startRun(profile.id);
      navigate(`/audit-export/runs/${run.id}`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      setError(msg);
      setSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Neues Audit-Export-Profile (Schritt {step} / 5)</CardTitle>
        <p className="text-sm text-muted-foreground mt-1">
          Vaeren erzeugt aus diesem Profile eine Audit-Mappe mit PDF, OSCAL-JSON
          und HMAC-signiertem ZIP-Bundle.
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {step === 1 && (
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Profile-Name</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="z. B. ISO-27001 Q4 2026"
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
                />
              </div>
              <div>
                <Label htmlFor="to">Zeitraum bis</Label>
                <Input
                  id="to"
                  type="date"
                  value={zeitraumBis}
                  onChange={(e) => setZeitraumBis(e.target.value)}
                />
              </div>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-2">
            <Label>Norm-Scope (mindestens eine auswählen)</Label>
            <div className="grid grid-cols-2 gap-2">
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
        )}

        {step === 3 && (
          <div className="space-y-2">
            <Label>Audit-Template</Label>
            <div className="space-y-1">
              {ALL_TEMPLATES.map((t) => (
                <label key={t} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="template"
                    checked={template === t}
                    onChange={() => setTemplate(t)}
                  />
                  {TEMPLATE_LABEL[t]}
                </label>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="space-y-4">
            <div>
              <Label>Belege im Bundle</Label>
              <div className="space-y-1">
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="evidence-mode"
                    checked={evidenceMode === "embed"}
                    onChange={() => setEvidenceMode("embed")}
                  />
                  Original-Dateien einbetten (größer, eigenständig)
                </label>
                <label className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="evidence-mode"
                    checked={evidenceMode === "reference"}
                    onChange={() => setEvidenceMode("reference")}
                  />
                  Nur Hash-Referenzen (kleiner, benötigt Vaeren-Zugriff)
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
          </div>
        )}

        {step === 5 && (
          <div className="space-y-3">
            <h3 className="text-base font-semibold">Zusammenfassung</h3>
            <ul className="text-sm space-y-1">
              <li>
                <strong>Name:</strong> {name}
              </li>
              <li>
                <strong>Zeitraum:</strong> {zeitraumVon} – {zeitraumBis}
              </li>
              <li>
                <strong>Norm-Scope:</strong>{" "}
                {normScope.map((n) => NORM_LABEL[n]).join(", ")}
              </li>
              <li>
                <strong>Template:</strong> {TEMPLATE_LABEL[template]}
              </li>
              <li>
                <strong>Evidence-Mode:</strong> {evidenceMode}
              </li>
              <li>
                <strong>Anonymisierung:</strong>{" "}
                {anonymisierenPii ? "an" : "aus"}
              </li>
              <li>
                <strong>Wasserzeichen:</strong>{" "}
                {watermarkDraft ? "an" : "aus"}
              </li>
            </ul>
            {error && <p className="text-destructive text-sm">{error}</p>}
          </div>
        )}

        <div className="flex justify-between border-t pt-4">
          <Button
            variant="outline"
            disabled={step === 1 || submitting}
            onClick={() => setStep(step - 1)}
          >
            Zurück
          </Button>
          {step < 5 && (
            <Button disabled={!canNext} onClick={() => setStep(step + 1)}>
              Weiter
            </Button>
          )}
          {step === 5 && (
            <Button disabled={submitting} onClick={submit}>
              {submitting ? "Run wird gestartet …" : "Profile speichern & Run starten"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
