/**
 * 5-Step-Wizard zum Anlegen eines AuditExportProfile.
 *
 * Steps: 1 Name+Zeitraum → 2 Norm-Scope → 3 Template → 4 Optionen → 5 Preview+Generate.
 *
 * Step 5 ruft beim Einstieg `POST /profiles/` (Save) + `POST /profiles/:id/preview/`
 * (Preview-API) und zeigt erwartete Record-Count + Bundle-Size, damit der User vor
 * "Run starten" sieht ob überhaupt Daten im Zeitraum sind.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createProfile,
  NORM_LABEL,
  previewRun,
  startRun,
  TEMPLATE_LABEL,
  type AuditExportProfile,
  type AuditTemplate,
  type EvidenceMode,
  type NormScope,
  type RunPreview,
} from "@/lib/api/audit_export";
import { ALL_NORMS, ALL_TEMPLATES } from "@/lib/api/audit_export_constants";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

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

  // Preview-State für Step 5
  const [savedProfile, setSavedProfile] = useState<AuditExportProfile | null>(
    null,
  );
  const [preview, setPreview] = useState<RunPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

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

  // Auto-Save + Preview wenn Step 5 erreicht wird (genau einmal pro Profile-Konfiguration)
  useEffect(() => {
    if (step !== 5) return;
    if (savedProfile) return; // Bereits gespeichert
    let cancelled = false;

    (async () => {
      setPreviewLoading(true);
      setPreviewError(null);
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
        if (cancelled) return;
        setSavedProfile(profile);
        const pv = await previewRun(profile.id);
        if (cancelled) return;
        setPreview(pv);
      } catch (e: unknown) {
        if (cancelled) return;
        const msg = e instanceof Error ? e.message : String(e);
        setPreviewError(msg);
      } finally {
        if (!cancelled) setPreviewLoading(false);
      }
    })();

    return () => {
      cancelled = true;
    };
    // Bewusst nur step + savedProfile als Trigger — Felder ändern sich nicht
    // mehr nach Step 5 (Zurück-Button setzt savedProfile NICHT zurück, d. h.
    // bei zurück+vor wird die alte Speicherung verwendet).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [step]);

  const submit = async () => {
    if (!savedProfile) {
      setError("Profile noch nicht gespeichert — bitte kurz warten.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const run = await startRun(savedProfile.id);
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

            <div className="border-t pt-3">
              <h4 className="text-sm font-semibold">Vorab-Schätzung</h4>
              {previewLoading && (
                <p className="text-sm text-muted-foreground">
                  Berechne Vorschau …
                </p>
              )}
              {previewError && (
                <p className="text-sm text-destructive">
                  Vorschau fehlgeschlagen: {previewError}
                </p>
              )}
              {preview && (
                <div className="text-sm space-y-1 mt-1">
                  <p>
                    <strong>Erwartete Belege:</strong> {preview.evidence_count}
                  </p>
                  <p>
                    <strong>Geschätzte Bundle-Größe:</strong>{" "}
                    {preview.geschaetzte_groesse_kb} KB
                  </p>
                  {preview.evidence_count === 0 && (
                    <p className="rounded border-l-4 border-amber-500 bg-amber-50 p-2 text-amber-900">
                      Achtung: Keine Belege im gewählten Zeitraum gefunden. Run
                      würde eine leere Mappe erzeugen. Eventuell Zeitraum oder
                      Norm-Scope anpassen.
                    </p>
                  )}
                  {Object.keys(preview.counts_per_aggregator || {}).length >
                    0 && (
                    <details className="mt-1 text-xs">
                      <summary className="cursor-pointer">
                        Detail pro Aggregator
                      </summary>
                      <ul className="ml-4 mt-1 space-y-0.5">
                        {Object.entries(preview.counts_per_aggregator).map(
                          ([slug, cnt]) => (
                            <li key={slug}>
                              {slug}: {cnt}
                            </li>
                          ),
                        )}
                      </ul>
                    </details>
                  )}
                </div>
              )}
            </div>

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
            <Button
              disabled={submitting || previewLoading || !savedProfile}
              onClick={submit}
            >
              {submitting ? "Run wird gestartet …" : "Run starten"}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
