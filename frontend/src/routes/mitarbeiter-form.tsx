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
  type MitarbeiterInput,
  useCreateMitarbeiter,
  useMitarbeiter,
  useUpdateMitarbeiter,
} from "@/lib/api/mitarbeiter";
import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";

export const mitarbeiterSchema = z.object({
  vorname: z.string().min(1, "Pflichtfeld"),
  nachname: z.string().min(1, "Pflichtfeld"),
  email: z.string().email("Bitte gültige E-Mail.").or(z.literal("")).optional(),
  abteilung: z.string().min(1, "Pflichtfeld"),
  rolle: z.string().min(1, "Pflichtfeld"),
  eintritt: z.string().min(1, "Pflichtfeld"),
  austritt: z.string().optional().nullable(),
  external_id: z.string().optional(),
});

export type MitarbeiterFormValues = z.infer<typeof mitarbeiterSchema>;

export function MitarbeiterFormPage() {
  const { id } = useParams<{ id?: string }>();
  const numericId = id ? Number.parseInt(id, 10) : undefined;
  const navigate = useNavigate();

  const existing = useMitarbeiter(numericId);
  const create = useCreateMitarbeiter();
  const update = useUpdateMitarbeiter(numericId ?? 0);

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    formState: { errors },
  } = useForm<MitarbeiterFormValues>({
    resolver: zodResolver(mitarbeiterSchema),
    defaultValues: {
      vorname: "",
      nachname: "",
      email: "",
      abteilung: "",
      rolle: "",
      eintritt: "",
      austritt: "",
      external_id: "",
    },
  });

  useEffect(() => {
    if (existing.data) {
      setValue("vorname", existing.data.vorname);
      setValue("nachname", existing.data.nachname);
      setValue("email", existing.data.email);
      setValue("abteilung", existing.data.abteilung);
      setValue("rolle", existing.data.rolle);
      setValue("eintritt", existing.data.eintritt);
      setValue("austritt", existing.data.austritt ?? "");
      setValue("external_id", existing.data.external_id ?? "");
    }
  }, [existing.data, setValue]);

  const handleApiError = (err: ApiError) => {
    if (err.status === 400 && err.body && typeof err.body === "object") {
      for (const [field, messages] of Object.entries(
        err.body as Record<string, string[]>,
      )) {
        if (Array.isArray(messages) && messages[0]) {
          setError(field as keyof MitarbeiterFormValues, {
            message: messages[0],
          });
        }
      }
      toast.error("Validierungsfehler.");
    } else if (err.status === 403) {
      toast.error("Keine Berechtigung.");
    } else {
      toast.error("Server-Fehler.");
    }
  };

  const onSubmit = handleSubmit((values) => {
    const payload: MitarbeiterInput = {
      vorname: values.vorname,
      nachname: values.nachname,
      email: values.email ?? "",
      abteilung: values.abteilung,
      rolle: values.rolle,
      eintritt: values.eintritt,
      austritt: values.austritt || null,
      external_id: values.external_id || "",
    };
    if (numericId !== undefined) {
      update.mutate(payload, {
        onSuccess: () => {
          toast.success("Aktualisiert.");
          navigate("/mitarbeiter");
        },
        onError: handleApiError,
      });
    } else {
      create.mutate(payload, {
        onSuccess: () => {
          toast.success("Angelegt.");
          navigate("/mitarbeiter");
        },
        onError: handleApiError,
      });
    }
  });

  const pending = create.isPending || update.isPending;
  const isEdit = numericId !== undefined;

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {isEdit ? "Mitarbeiter bearbeiten" : "Neuer Mitarbeiter"}
        </CardTitle>
      </CardHeader>
      <form onSubmit={onSubmit}>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="vorname">Vorname</Label>
              <Input id="vorname" {...register("vorname")} />
              {errors.vorname && (
                <p className="text-xs text-destructive">
                  {errors.vorname.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="nachname">Nachname</Label>
              <Input id="nachname" {...register("nachname")} />
              {errors.nachname && (
                <p className="text-xs text-destructive">
                  {errors.nachname.message}
                </p>
              )}
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">E-Mail (optional)</Label>
            <Input id="email" type="email" {...register("email")} />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="abteilung">Abteilung</Label>
              <Input
                id="abteilung"
                {...register("abteilung")}
                placeholder="z. B. Produktion"
              />
              {errors.abteilung && (
                <p className="text-xs text-destructive">
                  {errors.abteilung.message}
                </p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="rolle">Rolle / Tätigkeit</Label>
              <Input
                id="rolle"
                {...register("rolle")}
                placeholder="z. B. Maschinenführer:in"
              />
              {errors.rolle && (
                <p className="text-xs text-destructive">
                  {errors.rolle.message}
                </p>
              )}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="eintritt">Eintrittsdatum</Label>
              <Input id="eintritt" type="date" {...register("eintritt")} />
              {errors.eintritt && (
                <p className="text-xs text-destructive">
                  {errors.eintritt.message}
                </p>
              )}
            </div>
            {isEdit && (
              <div className="space-y-2">
                <Label htmlFor="austritt">Austrittsdatum (optional)</Label>
                <Input id="austritt" type="date" {...register("austritt")} />
                {errors.austritt && (
                  <p className="text-xs text-destructive">
                    {errors.austritt.message}
                  </p>
                )}
              </div>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="external_id">Externe ID (optional, ERP-Sync)</Label>
            <Input id="external_id" {...register("external_id")} />
          </div>
        </CardContent>
        <CardFooter className="gap-2">
          <Button type="submit" disabled={pending}>
            {pending ? "Speichere …" : "Speichern"}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => navigate("/mitarbeiter")}
          >
            Abbrechen
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
