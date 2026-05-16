import { type AuthUser, useAuthStore } from "@/lib/stores/auth-store";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { ApiError, _resetCsrfCacheForTests, api } from "./client";

export interface LoginPayload {
  email: string;
  password: string;
}

export interface LoginMfaRequiredResponse {
  detail: "mfa_required";
  ephemeral_token: string;
}

export type LoginResponse = AuthUser | LoginMfaRequiredResponse;

export function isMfaRequired(
  resp: LoginResponse | undefined,
): resp is LoginMfaRequiredResponse {
  return (
    !!resp &&
    typeof resp === "object" &&
    "detail" in resp &&
    resp.detail === "mfa_required" &&
    "ephemeral_token" in resp
  );
}

export function useCurrentUser() {
  const setUser = useAuthStore((s) => s.setUser);
  return useQuery<AuthUser, ApiError>({
    queryKey: ["me"],
    queryFn: async () => {
      const u = await api<AuthUser>("/api/auth/user/");
      setUser(u);
      return u;
    },
  });
}

export function useLogin() {
  const navigate = useNavigate();
  const setUser = useAuthStore((s) => s.setUser);
  const setMfaChallenge = useAuthStore((s) => s.setMfaChallenge);
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, LoginPayload>({
    mutationFn: async (payload) => {
      try {
        return await api<AuthUser>("/api/auth/login/", {
          method: "POST",
          json: payload,
        });
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          const body = err.body as Partial<LoginMfaRequiredResponse>;
          if (body && body.detail === "mfa_required" && body.ephemeral_token) {
            return {
              detail: "mfa_required",
              ephemeral_token: body.ephemeral_token,
            };
          }
        }
        throw err;
      }
    },
    onSuccess: async (data) => {
      const resp = data as LoginResponse | undefined;
      if (isMfaRequired(resp)) {
        setMfaChallenge(resp.ephemeral_token);
        navigate("/mfa-challenge");
        return;
      }
      // Backend antwortet mit 204 (kein Body) → User über /api/auth/user/ holen.
      try {
        const me = await api<AuthUser>("/api/auth/user/");
        setUser(me);
      } catch {
        // Fallthrough: ProtectedRoute holt den User selbst nach.
      }
      queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/");
    },
  });
}

export function useLogout() {
  const navigate = useNavigate();
  const clear = useAuthStore((s) => s.clear);
  const queryClient = useQueryClient();

  const finish = () => {
    clear();
    queryClient.clear();
    _resetCsrfCacheForTests(); // CSRF-Token-Cache leeren — sonst nutzt der nächste Login einen stale Token
    navigate("/login");
  };

  return useMutation<unknown, ApiError, void>({
    mutationFn: async () => {
      try {
        return await api("/api/auth/logout/", { method: "POST" });
      } catch (err) {
        // Backend-Logout darf nicht den Client-State blockieren — wenn die
        // Server-Session bereits ungültig ist (CSRF-Rotation, abgelaufen,
        // konkurrierender Logout), würden wir sonst hängen bleiben.
        if (
          err instanceof ApiError &&
          (err.status === 401 || err.status === 403)
        ) {
          return undefined;
        }
        throw err;
      }
    },
    onSuccess: finish,
    onError: () => {
      // Auch bei Netzwerk-/5xx-Fehler: lokal abmelden + navigieren. Der
      // User darf nicht im halb-eingeloggten Zustand stehen bleiben.
      toast.error("Abmeldung serverseitig fehlgeschlagen — lokal abgemeldet.");
      finish();
    },
  });
}

export interface MfaSetupResponse {
  secret: string;
  qr_url: string;
}

export function useMfaSetup() {
  return useMutation<MfaSetupResponse, ApiError, void>({
    mutationFn: () =>
      api<MfaSetupResponse>("/api/auth/mfa/totp/setup/", { method: "POST" }),
  });
}

export interface MfaVerifyResponse {
  recovery_codes: string[];
}

export function useMfaVerify() {
  return useMutation<MfaVerifyResponse, ApiError, { code: string }>({
    mutationFn: (payload) =>
      api<MfaVerifyResponse>("/api/auth/mfa/totp/verify/", {
        method: "POST",
        json: payload,
      }),
  });
}

export function useMfaLogin() {
  const navigate = useNavigate();
  const ephemeralToken = useAuthStore((s) => s.ephemeralToken);
  const setUser = useAuthStore((s) => s.setUser);
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, { code: string }>({
    mutationFn: ({ code }) => {
      if (!ephemeralToken) {
        throw new ApiError(400, { detail: "kein ephemeraler Token" });
      }
      return api("/api/auth/mfa/login/", {
        method: "POST",
        json: { ephemeral_token: ephemeralToken, code },
      });
    },
    onSuccess: async () => {
      const me = await api<AuthUser>("/api/auth/user/");
      setUser(me);
      queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/mitarbeiter");
    },
  });
}
