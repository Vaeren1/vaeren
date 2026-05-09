import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { z } from "zod";
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
import { ApiError } from "@/lib/api/client";
import {
  type MitarbeiterInput,
  useCreateMitarbeiter,
  useMitarbeiter,
  useUpdateMitarbeiter,
} from "@/lib/api/mitarbeiter";

export const mitarbeiterSchema = z.object({
  vorname: z.string().min(1, "Pflichtfeld"),
  nachname: z.string().min(1, "Pflichtfeld"),
  email: z.string().email("Bitte gültige E-Mail."),
  abteilung: z.string().min(1, "Pflichtfeld"),
  externe_id: z.string().optional().nullable(),
  aktiv: z.boolean().default(true),
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
      externe_id: "",
      aktiv: true,
    },
  });

  useEffect(() => {
    if (existing.data) {
      setValue("vorname", existing.data.vorname);
      setValue("nachname", existing.data.nachname);
      setValue("email", existing.data.email);
      setValue("abteilung", existing.data.abteilung);
      setValue("externe_id", existing.data.externe_id ?? "");
      setValue("aktiv", existing.data.aktiv);
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
      ...values,
      externe_id: values.externe_id || null,
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

  return (
    <Card>
      <CardHeader>
        <CardTitle>
          {numericId !== undefined ? "Mitarbeiter bearbeiten" : "Neuer Mitarbeiter"}
        </CardTitle>
      </CardHeader>
      <form onSubmit={onSubmit}>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="vorname">Vorname</Label>
              <Input id="vorname" {...register("vorname")} />
              {errors.vorname && (
                <p className="text-xs text-destructive">{errors.vorname.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="nachname">Nachname</Label>
              <Input id="nachname" {...register("nachname")} />
              {errors.nachname && (
                <p className="text-xs text-destructive">{errors.nachname.message}</p>
              )}
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">E-Mail</Label>
            <Input id="email" type="email" {...register("email")} />
            {errors.email && (
              <p className="text-xs text-destructive">{errors.email.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="abteilung">Abteilung</Label>
            <Input id="abteilung" {...register("abteilung")} />
            {errors.abteilung && (
              <p className="text-xs text-destructive">{errors.abteilung.message}</p>
            )}
          </div>
          <div className="space-y-2">
            <Label htmlFor="externe_id">Externe ID (optional)</Label>
            <Input id="externe_id" {...register("externe_id")} />
          </div>
          <div className="flex items-center gap-2">
            <input
              id="aktiv"
              type="checkbox"
              className="h-4 w-4"
              {...register("aktiv")}
            />
            <Label htmlFor="aktiv">Aktiv</Label>
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
