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
import { useMfaSetup, useMfaVerify } from "@/lib/api/auth";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

interface FormValues {
  code: string;
}

export function MfaSetupPage() {
  const setup = useMfaSetup();
  const verify = useMfaVerify();
  const [recoveryCodes, setRecoveryCodes] = useState<string[] | null>(null);

  // Setup automatisch beim Mount triggern, damit Konrad sofort QR-Code sieht
  useEffect(() => {
    if (!setup.data && !setup.isPending) {
      setup.mutate();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const { register, handleSubmit } = useForm<FormValues>({
    defaultValues: { code: "" },
  });

  const onSubmit = handleSubmit((values) => {
    verify.mutate(values, {
      onSuccess: (data) => {
        setRecoveryCodes(data.recovery_codes);
        toast.success("MFA aktiviert.");
      },
      onError: () => toast.error("Code falsch oder abgelaufen."),
    });
  });

  if (recoveryCodes) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recovery-Codes</CardTitle>
          <CardDescription>
            Bitte ausdrucken oder im Passwort-Manager speichern. Jeder Code ist
            nur einmal verwendbar und ersetzt einen Authenticator-Code.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ul className="grid grid-cols-2 gap-2 font-mono text-sm">
            {recoveryCodes.map((c) => (
              <li key={c} className="rounded border bg-muted px-2 py-1">
                {c}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>MFA einrichten (TOTP)</CardTitle>
        <CardDescription>
          Authenticator-App (Google Authenticator, Authy, 1Password) öffnen,
          QR-Code scannen, dann den 6-stelligen Code unten eingeben.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {setup.isPending && <p>QR-Code wird generiert …</p>}
        {setup.data && (
          <div className="space-y-2">
            <p className="text-sm font-medium">Otpauth-URL:</p>
            <code className="block break-all rounded bg-muted p-2 text-xs">
              {setup.data.qr_url}
            </code>
            <p className="text-xs text-muted-foreground">
              Secret: <span className="font-mono">{setup.data.secret}</span>
            </p>
          </div>
        )}
        <form onSubmit={onSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="code">Authenticator-Code</Label>
            <Input
              id="code"
              inputMode="numeric"
              autoComplete="one-time-code"
              maxLength={6}
              {...register("code", { required: true, pattern: /^\d{6}$/ })}
            />
          </div>
          <CardFooter className="px-0">
            <Button type="submit" disabled={verify.isPending || !setup.data}>
              {verify.isPending ? "Prüfe …" : "MFA aktivieren"}
            </Button>
          </CardFooter>
        </form>
      </CardContent>
    </Card>
  );
}
