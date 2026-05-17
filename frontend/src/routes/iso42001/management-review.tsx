/**
 * Management-Review (ISO 42001 Kap. 9.3).
 */

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createManagementReview,
  listManagementReviews,
} from "@/lib/api/iso42001";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";

export function Iso42001ManagementReviewPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["iso42001-management-reviews"],
    queryFn: listManagementReviews,
  });
  const [showForm, setShowForm] = useState(false);

  const createMut = useMutation({
    mutationFn: createManagementReview,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["iso42001-management-reviews"] });
      qc.invalidateQueries({ queryKey: ["iso42001-dashboard"] });
      toast.success("Management-Review erfasst.");
      setShowForm(false);
    },
    onError: (e: unknown) => {
      toast.error(e instanceof Error ? e.message : "Erfassung fehlgeschlagen");
    },
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">AIMS Management-Review</h1>
          <p className="text-sm text-muted-foreground">
            ISO 42001 Kap. 9.3 — jährliche Überprüfung des KI-Management-Systems durch
            die Geschäftsführung.
          </p>
        </div>
        <Button onClick={() => setShowForm(true)}>+ Neue Review erfassen</Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Reviews</CardTitle>
        </CardHeader>
        <CardContent>
          {!data || data.results.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Noch keine Management-Review erfasst.
            </p>
          ) : (
            <ul className="divide-y">
              {data.results.map((r) => (
                <li key={r.id} className="py-2">
                  <div className="font-medium">Review {r.durchgefuehrt_am}</div>
                  <div className="text-xs text-muted-foreground">
                    Teilnehmer: {r.teilnehmer} · Nächste Review:{" "}
                    {r.naechste_review_faellig_am}
                  </div>
                  <div className="mt-1 text-sm">{r.entscheidungen}</div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {showForm && (
        <ReviewForm
          onCancel={() => setShowForm(false)}
          onSubmit={(p) => createMut.mutate(p)}
          isPending={createMut.isPending}
        />
      )}
    </div>
  );
}

function ReviewForm({
  onCancel,
  onSubmit,
  isPending,
}: {
  onCancel: () => void;
  onSubmit: (p: {
    durchgefuehrt_am: string;
    teilnehmer: string;
    inputs_zusammenfassung: string;
    entscheidungen: string;
  }) => void;
  isPending: boolean;
}) {
  const [datum, setDatum] = useState(new Date().toISOString().slice(0, 10));
  const [teilnehmer, setTeilnehmer] = useState("");
  const [inputs, setInputs] = useState("");
  const [entscheidungen, setEntscheidungen] = useState("");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30">
      <form
        className="w-[640px] max-w-full rounded-md bg-white p-6 shadow-xl"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit({
            durchgefuehrt_am: datum,
            teilnehmer,
            inputs_zusammenfassung: inputs,
            entscheidungen,
          });
        }}
      >
        <h2 className="mb-3 text-lg font-semibold">Neue Management-Review</h2>
        <div className="space-y-3">
          <div>
            <Label>Durchgeführt am</Label>
            <Input
              type="date"
              value={datum}
              onChange={(e) => setDatum(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Teilnehmer (Freitext)</Label>
            <textarea
              rows={2}
              className="w-full rounded border px-3 py-2 text-sm"
              value={teilnehmer}
              onChange={(e) => setTeilnehmer(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Inputs-Zusammenfassung</Label>
            <textarea
              rows={3}
              className="w-full rounded border px-3 py-2 text-sm"
              placeholder="Incidents, AIIAs, Kennzahlen, Audit-Ergebnisse ..."
              value={inputs}
              onChange={(e) => setInputs(e.target.value)}
              required
            />
          </div>
          <div>
            <Label>Entscheidungen</Label>
            <textarea
              rows={3}
              className="w-full rounded border px-3 py-2 text-sm"
              value={entscheidungen}
              onChange={(e) => setEntscheidungen(e.target.value)}
              required
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <Button type="button" variant="outline" onClick={onCancel}>
            Abbrechen
          </Button>
          <Button type="submit" disabled={isPending}>
            Erfassen
          </Button>
        </div>
      </form>
    </div>
  );
}
