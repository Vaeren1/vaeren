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
import type { ApiError } from "@/lib/api/client";
import {
  KATEGORIE_LABEL,
  KATEGORIE_ORDER,
  type Kategorie,
  type KursInput,
  type QuizModus,
  useCreateKurs,
  useKurs,
  useUpdateKurs,
} from "@/lib/api/schulungen";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

export const kursSchema = z
  .object({
    titel: z.string().min(1, "Pflichtfeld").max(200),
    beschreibung: z.string().max(2000).optional().default(""),
    kategorie: z.enum([
      "arbeitsschutz",
      "brandschutz",
      "gefahrstoffe",
      "datenschutz",
      "compliance",
      "umwelt",
      "sonstiges",
    ]),
    quiz_modus: z.enum(["quiz", "kenntnisnahme", "kenntnisnahme_lesezeit"]),
    fragen_pro_quiz: z.number().int().min(0).max(100),
    min_richtig_prozent: z.number().int().min(0).max(100),
    mindest_lesezeit_s: z.number().int().min(0).max(7200),
    zertifikat_aktiv: z.boolean(),
    gueltigkeit_monate: z.number().int().min(1).max(120),
    aktiv: z.boolean(),
  })
  .refine(
    (v) =>
      v.quiz_modus !== "kenntnisnahme_lesezeit" || v.mindest_lesezeit_s > 0,
    {
      path: ["mindest_lesezeit_s"],
      message: "Bei Modus 'Kenntnisnahme + Lesezeit' > 0 erforderlich.",
    },
  );

export type KursFormValues = z.infer<typeof kursSchema>;

const DEFAULTS: KursFormValues = {
  titel: "",
  beschreibung: "",
  kategorie: "sonstiges",
  quiz_modus: "quiz",
  fragen_pro_quiz: 10,
  min_richtig_prozent: 80,
  mindest_lesezeit_s: 0,
  zertifikat_aktiv: true,
  gueltigkeit_monate: 12,
  aktiv: true,
};

export function KursFormPage() {
  const { id } = useParams<{ id?: string }>();
  const numericId = id ? Number.parseInt(id, 10) : undefined;
  const navigate = useNavigate();

  const existing = useKurs(numericId);
  const create = useCreateKurs();
  const update = useUpdateKurs(numericId ?? 0);

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    watch,
    formState: { errors },
  } = useForm<KursFormValues>({
    resolver: zodResolver(kursSchema),
    defaultValues: DEFAULTS,
  });

  const quizModus = watch("quiz_modus");

  useEffect(() => {
    if (existing.data) {
      setValue("titel", existing.data.titel);
      setValue("beschreibung", existing.data.beschreibung);
      setValue("kategorie", existing.data.kategorie);
      setValue("quiz_modus", existing.data.quiz_modus);
      setValue("fragen_pro_quiz", existing.data.fragen_pro_quiz);
      setValue("min_richtig_prozent", existing.data.min_richtig_prozent);
      setValue("mindest_lesezeit_s", existing.data.mindest_lesezeit_s);
      setValue("zertifikat_aktiv", existing.data.zertifikat_aktiv);
      setValue("gueltigkeit_monate", existing.data.gueltigkeit_monate);
      setValue("aktiv", existing.data.aktiv);
    }
  }, [existing.data, setValue]);

  const handleApiError = (err: ApiError) => {
    if (err.body && typeof err.body === "object") {
      for (const [field, msgs] of Object.entries(err.body)) {
        const msg = Array.isArray(msgs) ? String(msgs[0]) : String(msgs);
        setError(field as keyof KursFormValues, { message: msg });
      }
    }
    toast.error("Speichern fehlgeschlagen — bitte Felder prüfen.");
  };

  const onSubmit = (values: KursFormValues) => {
    const payload: KursInput = {
      ...values,
      beschreibung: values.beschreibung ?? "",
      fragen_pro_quiz: values.quiz_modus === "quiz" ? values.fragen_pro_quiz : 0,
      min_richtig_prozent:
        values.quiz_modus === "quiz" ? values.min_richtig_prozent : 0,
      mindest_lesezeit_s:
        values.quiz_modus === "kenntnisnahme_lesezeit"
          ? values.mindest_lesezeit_s
          : 0,
    };
    const onSuccess = (kurs: { id: number }) => {
      toast.success("Kurs gespeichert.");
      navigate(`/kurse/${kurs.id}`);
    };
    if (numericId) {
      update.mutate(payload, { onSuccess, onError: handleApiError });
    } else {
      create.mutate(payload, { onSuccess, onError: handleApiError });
    }
  };

  const isStandardCatalog = existing.data?.ist_standardkatalog === true;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {numericId ? "Kurs bearbeiten" : "Neuer Kurs"}
        </CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {isStandardCatalog && (
            <p className="rounded border-l-4 border-amber-500 bg-amber-50 p-3 text-sm">
              Standard-Katalog-Kurse können nicht bearbeitet werden.
            </p>
          )}

          <div>
            <Label htmlFor="titel">Titel *</Label>
            <Input
              id="titel"
              {...register("titel")}
              disabled={isStandardCatalog}
            />
            {errors.titel && (
              <p className="text-sm text-destructive">{errors.titel.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="beschreibung">Beschreibung</Label>
            <textarea
              id="beschreibung"
              className="block w-full rounded border border-input bg-background p-2 text-sm"
              rows={3}
              {...register("beschreibung")}
              disabled={isStandardCatalog}
            />
          </div>

          <div>
            <Label htmlFor="kategorie">Kategorie *</Label>
            <select
              id="kategorie"
              className="block w-full rounded border border-input bg-background p-2 text-sm"
              {...register("kategorie")}
              disabled={isStandardCatalog}
            >
              {KATEGORIE_ORDER.map((k: Kategorie) => (
                <option key={k} value={k}>
                  {KATEGORIE_LABEL[k]}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-muted-foreground">
              Bestimmt die Gruppierung in der Kurs-Bibliothek.
            </p>
          </div>

          <fieldset className="rounded border p-3">
            <legend className="px-1 text-sm font-medium">Abschluss-Modus</legend>
            <div className="space-y-2">
              {(
                [
                  ["quiz", "Quiz mit Single-Choice-Fragen"],
                  ["kenntnisnahme", "Nur Kenntnisnahme-Button am Ende"],
                  [
                    "kenntnisnahme_lesezeit",
                    "Kenntnisnahme + Mindest-Lesezeit pro Modul",
                  ],
                ] as [QuizModus, string][]
              ).map(([value, label]) => (
                <label key={value} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    value={value}
                    {...register("quiz_modus")}
                    disabled={isStandardCatalog}
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>

          {quizModus === "quiz" && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="fragen_pro_quiz">Fragen pro Quiz</Label>
                <Input
                  id="fragen_pro_quiz"
                  type="number"
                  min={1}
                  max={100}
                  {...register("fragen_pro_quiz", { valueAsNumber: true })}
                  disabled={isStandardCatalog}
                />
              </div>
              <div>
                <Label htmlFor="min_richtig_prozent">Bestehensschwelle (%)</Label>
                <Input
                  id="min_richtig_prozent"
                  type="number"
                  min={0}
                  max={100}
                  {...register("min_richtig_prozent", { valueAsNumber: true })}
                  disabled={isStandardCatalog}
                />
              </div>
            </div>
          )}

          {quizModus === "kenntnisnahme_lesezeit" && (
            <div>
              <Label htmlFor="mindest_lesezeit_s">
                Mindest-Lesezeit pro Modul (Sekunden)
              </Label>
              <Input
                id="mindest_lesezeit_s"
                type="number"
                min={1}
                {...register("mindest_lesezeit_s", { valueAsNumber: true })}
                disabled={isStandardCatalog}
              />
              {errors.mindest_lesezeit_s && (
                <p className="text-sm text-destructive">
                  {errors.mindest_lesezeit_s.message}
                </p>
              )}
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <div>
              <Label htmlFor="gueltigkeit_monate">Gültigkeit (Monate)</Label>
              <Input
                id="gueltigkeit_monate"
                type="number"
                min={1}
                max={120}
                {...register("gueltigkeit_monate", { valueAsNumber: true })}
                disabled={isStandardCatalog}
              />
            </div>
            <div className="flex flex-col gap-2 pt-6">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  {...register("zertifikat_aktiv")}
                  disabled={isStandardCatalog}
                />
                Zertifikat-PDF nach Abschluss generieren
              </label>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  {...register("aktiv")}
                  disabled={isStandardCatalog}
                />
                Kurs aktiv (in Liste verwendbar)
              </label>
            </div>
          </div>
        </CardContent>
        <CardFooter className="flex justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/kurse")}
          >
            Abbrechen
          </Button>
          <Button
            type="submit"
            disabled={create.isPending || update.isPending || isStandardCatalog}
          >
            {numericId ? "Speichern" : "Anlegen"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
