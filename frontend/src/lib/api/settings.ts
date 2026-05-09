import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export interface TenantSettings {
  schema_name: string;
  firma_name: string;
  locale: string;
  plan: string;
  pilot: boolean;
  mfa_required: boolean;
}

export function useTenantSettings() {
  return useQuery<TenantSettings, ApiError>({
    queryKey: ["tenant-settings"],
    queryFn: () => api<TenantSettings>("/api/tenant/settings/"),
  });
}

export function useUpdateTenantSettings() {
  const qc = useQueryClient();
  return useMutation<TenantSettings, ApiError, Partial<TenantSettings>>({
    mutationFn: (payload) =>
      api<TenantSettings>("/api/tenant/settings/", {
        method: "PATCH",
        json: payload,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tenant-settings"] });
    },
  });
}
