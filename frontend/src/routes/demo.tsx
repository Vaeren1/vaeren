import { zodResolver } from "@hookform/resolvers/zod";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  type DemoRequestInput,
  type MitarbeiterAnzahl,
  useSubmitDemoRequest,
} from "@/lib/api/demo";

const sizeOptions: ReadonlyArray<{ value: MitarbeiterAnzahl; label: string }> =
  [
    { value: "<50", label: "unter 50" },
    { value: "50-120", label: "50–120" },
    { value: "121-250", label: "121–250" },
    { value: "251-500", label: "251–500" },
    { value: ">500", label: "über 500" },
  ];

export const demoSchema = z.object({
  firma: z.string().min(1, "Pflichtfeld"),
  vorname: z.string().min(1, "Pflichtfeld"),
  nachname: z.string().min(1, "Pflichtfeld"),
  email: z.string().email("Bitte gültige E-Mail."),
  telefon: z.string().optional(),
  mitarbeiter_anzahl: z
    .enum(["<50", "50-120", "121-250", "251-500", ">500", ""])
    .optional(),
  nachricht: z.string().max(2000, "Maximal 2000 Zeichen.").optional(),
  // Honeypot — Spam-Bots füllen Felder mit „url"/„website"-Namen.
  // Im Code 'aria-hidden' + CSS-versteckt, damit echte User es nicht sehen.
  website: z.string().optional(),
});

export type DemoFormValues = z.infer<typeof demoSchema>;

export function DemoPage() {
  const [submitted, setSubmitted] = useState(false);
  const submit = useSubmitDemoRequest();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DemoFormValues>({
    resolver: zodResolver(demoSchema),
    defaultValues: {
      firma: "",
      vorname: "",
      nachname: "",
      email: "",
      telefon: "",
      mitarbeiter_anzahl: "",
      nachricht: "",
      website: "",
    },
  });

  const onSubmit = handleSubmit((values) => {
    const payload: DemoRequestInput = {
      ...values,
      mitarbeiter_anzahl: values.mitarbeiter_anzahl ?? "",
    };
    submit.mutate(payload, {
      onSuccess: () => setSubmitted(true),
      onError: (err) => {
        if (err.status === 429) {
          toast.error("Zu viele Anfragen — bitte später erneut versuchen.");
        } else if (err.status === 400) {
          toast.error("Bitte Eingaben prüfen.");
        } else {
          toast.error("Server-Fehler.");
        }
      },
    });
  });

  if (submitted) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Vielen Dank!</CardTitle>
            <CardDescription>
              Wir melden uns innerhalb von 1 Werktag.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle>Demo anfragen</CardTitle>
          <CardDescription>
            Vaeren — Compliance-Autopilot für den Industrie-Mittelstand.
          </CardDescription>
        </CardHeader>
        <form onSubmit={onSubmit}>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="firma">Firma</Label>
                <Input id="firma" {...register("firma")} />
                {errors.firma && (
                  <p className="text-xs text-destructive">{errors.firma.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="mitarbeiter_anzahl">Mitarbeiter-Anzahl</Label>
                <select
                  id="mitarbeiter_anzahl"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  {...register("mitarbeiter_anzahl")}
                >
                  <option value="">— bitte wählen —</option>
                  {sizeOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
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
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="email">E-Mail</Label>
                <Input id="email" type="email" {...register("email")} />
                {errors.email && (
                  <p className="text-xs text-destructive">{errors.email.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="telefon">Telefon (optional)</Label>
                <Input id="telefon" type="tel" {...register("telefon")} />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="nachricht">Nachricht (optional)</Label>
              <Textarea id="nachricht" rows={4} {...register("nachricht")} />
              {errors.nachricht && (
                <p className="text-xs text-destructive">{errors.nachricht.message}</p>
              )}
            </div>
            {/* Honeypot — versteckt vor menschlichen Usern */}
            <div
              aria-hidden="true"
              className="absolute -left-[9999px]"
              style={{ position: "absolute", left: "-9999px" }}
            >
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                tabIndex={-1}
                autoComplete="off"
                {...register("website")}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button type="submit" disabled={submit.isPending} className="w-full">
              {submit.isPending ? "Wird gesendet …" : "Demo anfragen"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
