import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { type AuthUser, useAuthStore } from "@/lib/stores/auth-store";
import { ApiError, api } from "./client";

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
  resp: LoginResponse,
): resp is LoginMfaRequiredResponse {
  return (
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
            return { detail: "mfa_required", ephemeral_token: body.ephemeral_token };
          }
        }
        throw err;
      }
    },
    onSuccess: (data) => {
      const resp = data as LoginResponse;
      if (isMfaRequired(resp)) {
        setMfaChallenge(resp.ephemeral_token);
        navigate("/mfa-challenge");
        return;
      }
      setUser(resp as AuthUser);
      queryClient.invalidateQueries({ queryKey: ["me"] });
      navigate("/mitarbeiter");
    },
  });
}

export function useLogout() {
  const navigate = useNavigate();
  const clear = useAuthStore((s) => s.clear);
  const queryClient = useQueryClient();
  return useMutation<unknown, ApiError, void>({
    mutationFn: () => api("/api/auth/logout/", { method: "POST" }),
    onSuccess: () => {
      clear();
      queryClient.clear();
      navigate("/login");
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
