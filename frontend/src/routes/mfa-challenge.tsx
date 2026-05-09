import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Navigate } from "react-router-dom";
import { toast } from "sonner";
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
import { useMfaLogin } from "@/lib/api/auth";
import { useAuthStore } from "@/lib/stores/auth-store";

interface FormValues {
  code: string;
}

export function MfaChallengePage() {
  const ephemeralToken = useAuthStore((s) => s.ephemeralToken);
  const mfaLogin = useMfaLogin();
  const { register, handleSubmit, setFocus } = useForm<FormValues>({
    defaultValues: { code: "" },
  });

  useEffect(() => {
    setFocus("code");
  }, [setFocus]);

  if (!ephemeralToken) {
    return <Navigate to="/login" replace />;
  }

  const onSubmit = handleSubmit((values) => {
    mfaLogin.mutate(values, {
      onError: (err) => {
        if (err.status === 401) {
          toast.error("Code falsch oder abgelaufen.");
        } else {
          toast.error("Server-Fehler.");
        }
      },
    });
  });

  return (
    <div className="flex min-h-screen items-center justify-center bg-muted/40 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>MFA-Code eingeben</CardTitle>
          <CardDescription>
            Bitte den 6-stelligen Code aus deiner Authenticator-App eingeben.
          </CardDescription>
        </CardHeader>
        <form onSubmit={onSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="code">Authenticator-Code</Label>
              <Input
                id="code"
                inputMode="numeric"
                autoComplete="one-time-code"
                maxLength={6}
                {...register("code", {
                  required: true,
                  minLength: 6,
                  maxLength: 6,
                  pattern: /^\d{6}$/,
                })}
              />
            </div>
          </CardContent>
          <CardFooter>
            <Button
              type="submit"
              className="w-full"
              disabled={mfaLogin.isPending}
            >
              {mfaLogin.isPending ? "Prüfe …" : "Anmeldung abschließen"}
            </Button>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
