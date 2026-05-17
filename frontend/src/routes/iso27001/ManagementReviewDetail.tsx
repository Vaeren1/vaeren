/**
 * Management-Review-Detail-Seite: Inputs/Outputs-Editor + Vorbefüllen + PDF + Genehmigen.
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import {
  getMgtReview,
  mgtReviewPdfUrl,
  updateMgtReview,
  vorbefuelleMgtReviewInputs,
  type ManagementReview,
} from "@/lib/api/iso27001";
import { useMitarbeiterList } from "@/lib/api/mitarbeiter";
import { useAuthStore } from "@/lib/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { toast } from "sonner";

type Form = Pick<
  ManagementReview,
  | "inputs_audit_ergebnisse"
  | "inputs_findings_status"
  | "inputs_risiko_aenderungen"
  | "inputs_isms_performance"
  | "outputs_verbesserungen"
  | "outputs_ressourcen_bedarf"
  | "outputs_zielanpassungen"
  | "teilnehmer"
>;

const EMPTY: Form = {
  inputs_audit_ergebnisse: "",
  inputs_findings_status: "",
  inputs_risiko_aenderungen: "",
  inputs_isms_performance: "",
  outputs_verbesserungen: "",
  outputs_ressourcen_bedarf: "",
  outputs_zielanpassungen: "",
  teilnehmer: "",
};

export function Iso27001ManagementReviewDetail() {
  const params = useParams<{ id: string }>();
  const reviewId = Number(params.id);
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const isGf = user?.tenant_role === "geschaeftsfuehrer";

  const { data: review, isLoading } = useQuery({
    queryKey: ["iso27001-mgt-review", reviewId],
    queryFn: () => getMgtReview(reviewId),
    enabled: !Number.isNaN(reviewId),
  });
  const { data: mitarbeiter } = useMitarbeiterList();

  const [form, setForm] = useState<Form>(EMPTY);
  const [showGenehmigen, setShowGenehmigen] = useState(false);

  useEffect(() => {
    if (review) {
      setForm({
        inputs_audit_ergebnisse: review.inputs_audit_ergebnisse,
        inputs_findings_status: review.inputs_findings_status,
        inputs_risiko_aenderungen: review.inputs_risiko_aenderungen,
        inputs_isms_performance: review.inputs_isms_performance,
        outputs_verbesserungen: review.outputs_verbesserungen,
        outputs_ressourcen_bedarf: review.outputs_ressourcen_bedarf,
        outputs_zielanpassungen: review.outputs_zielanpassungen,
        teilnehmer: review.teilnehmer,
      });
    }
  }, [review]);

  const saveMut = useMutation({
    mutationFn: (payload: Partial<ManagementReview>) =>
      updateMgtReview(reviewId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-mgt-review", reviewId] });
      qc.invalidateQueries({ queryKey: ["iso27001-mgt-reviews"] });
      toast.success("Review gespeichert.");
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Speichern fehlgeschlagen"),
  });

  const vorbefuelleMut = useMutation({
    mutationFn: () => vorbefuelleMgtReviewInputs(reviewId),
    onSuccess: (updated) => {
      qc.setQueryData(["iso27001-mgt-review", reviewId], updated);
      qc.invalidateQueries({ queryKey: ["iso27001-mgt-reviews"] });
      toast.success("Inputs aus den letzten 12 Monaten vorbefüllt.");
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Vorbefüllen fehlgeschlagen"),
  });

  const genehmigenMut = useMutation({
    mutationFn: (mitarbeiterId: number) =>
      updateMgtReview(reviewId, {
        status: "genehmigt",
        beschlossen_von: mitarbeiterId,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso27001-mgt-review", reviewId] });
      qc.invalidateQueries({ queryKey: ["iso27001-mgt-reviews"] });
      toast.success("Review genehmigt.");
      setShowGenehmigen(false);
    },
    onError: (e: unknown) =>
      toast.error(e instanceof Error ? e.message : "Genehmigung fehlgeschlagen"),
  });

  if (isLoading || !review) {
    return <p>Lade …</p>;
  }

  function updateField<K extends keyof Form>(key: K, value: Form[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div className="space-y-4">
      <div>
        <Link to="/iso27001/management-review" className="text-sm underline">
          ← Review-Liste
        </Link>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle>Management-Review {review.review_jahr}</CardTitle>
              <p className="mt-1 text-sm text-muted-foreground">
                Status: <strong>{review.status}</strong> ·{" "}
                {review.durchgefuehrt_am
                  ? `Durchgeführt am ${review.durchgefuehrt_am}`
                  : "noch nicht durchgeführt"}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => vorbefuelleMut.mutate()}
                disabled={vorbefuelleMut.isPending}
              >
                Inputs vorbefüllen
              </Button>
              <a
                href={mgtReviewPdfUrl(reviewId)}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="outline">PDF herunterladen</Button>
              </a>
              {isGf && review.status === "durchgefuehrt" && (
                <Button onClick={() => setShowGenehmigen(true)}>
                  Genehmigen
                </Button>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Inputs (ISO 9.3.2)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <TextareaField
            label="Audit-Ergebnisse"
            value={form.inputs_audit_ergebnisse}
            onChange={(v) => updateField("inputs_audit_ergebnisse", v)}
          />
          <TextareaField
            label="Findings-Status"
            value={form.inputs_findings_status}
            onChange={(v) => updateField("inputs_findings_status", v)}
          />
          <TextareaField
            label="Risiko-Änderungen"
            value={form.inputs_risiko_aenderungen}
            onChange={(v) => updateField("inputs_risiko_aenderungen", v)}
          />
          <TextareaField
            label="ISMS-Performance"
            value={form.inputs_isms_performance}
            onChange={(v) => updateField("inputs_isms_performance", v)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Outputs (ISO 9.3.3)</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <TextareaField
            label="Verbesserungen"
            value={form.outputs_verbesserungen}
            onChange={(v) => updateField("outputs_verbesserungen", v)}
          />
          <TextareaField
            label="Ressourcen-Bedarf"
            value={form.outputs_ressourcen_bedarf}
            onChange={(v) => updateField("outputs_ressourcen_bedarf", v)}
          />
          <TextareaField
            label="Zielanpassungen"
            value={form.outputs_zielanpassungen}
            onChange={(v) => updateField("outputs_zielanpassungen", v)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Teilnehmer</CardTitle>
        </CardHeader>
        <CardContent>
          <textarea
            className="w-full rounded border px-3 py-2 text-sm"
            rows={3}
            value={form.teilnehmer}
            onChange={(e) => updateField("teilnehmer", e.target.value)}
            placeholder="Liste der Teilnehmer am Review."
          />
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button
          onClick={() => saveMut.mutate(form)}
          disabled={saveMut.isPending}
        >
          Review speichern
        </Button>
      </div>

      {showGenehmigen && (
        <GenehmigenDialog
          mitarbeiter={mitarbeiter?.results ?? []}
          onCancel={() => setShowGenehmigen(false)}
          onConfirm={(id) => genehmigenMut.mutate(id)}
          isPending={genehmigenMut.isPending}
        />
      )}
    </div>
  );
}

function TextareaField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <Label>{label}</Label>
      <textarea
        className="w-full rounded border px-3 py-2 text-sm"
        rows={4}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}

function GenehmigenDialog({
  mitarbeiter,
  onCancel,
  onConfirm,
  isPending,
}: {
  mitarbeiter: { id: number; vorname: string; nachname: string; rolle: string }[];
  onCancel: () => void;
  onConfirm: (mitarbeiterId: number) => void;
  isPending: boolean;
}) {
  const [id, setId] = useState<number | "">("");
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[480px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          if (id === "") {
            toast.error("Beschlossen von erforderlich.");
            return;
          }
          onConfirm(Number(id));
        }}
      >
        <h2 className="mb-2 text-lg font-semibold">Review genehmigen</h2>
        <p className="text-sm text-muted-foreground">
          Setzt den Status auf <strong>genehmigt</strong> und dokumentiert den
          beschließenden Geschäftsführer.
        </p>
        <div className="mt-3">
          <Label>Beschlossen von</Label>
          <select
            className="w-full rounded border px-3 py-2 text-sm"
            value={id}
            onChange={(e) => setId(e.target.value ? Number(e.target.value) : "")}
            required
          >
            <option value="">— Mitarbeiter wählen —</option>
            {mitarbeiter.map((m) => (
              <option key={m.id} value={m.id}>
                {m.vorname} {m.nachname} ({m.rolle})
              </option>
            ))}
          </select>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Genehmigen
          </Button>
        </div>
      </form>
    </div>
  );
}
