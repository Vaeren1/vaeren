import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type ApiError, api } from "./client";

export type NotificationStatus =
  | "geplant"
  | "versandt"
  | "geoeffnet"
  | "bounced"
  | "failed";

export interface Notification {
  id: number;
  channel: "email" | "in_app" | "sms";
  template: string;
  template_kontext: Record<string, unknown>;
  status: NotificationStatus;
  geplant_fuer: string | null;
  versandt_am: string | null;
  geoeffnet_am: string | null;
  created_at: string;
}

export function useNotificationList(enabled = true) {
  return useQuery<Notification[], ApiError>({
    queryKey: ["notifications"],
    queryFn: async () => {
      const res = await api<Notification[] | { results: Notification[] }>(
        "/api/notifications/",
      );
      return Array.isArray(res) ? res : res.results;
    },
    enabled,
  });
}

export function useUnreadCount() {
  return useQuery<{ unread: number }, ApiError>({
    queryKey: ["notifications-unread"],
    queryFn: () => api("/api/notifications/unread-count/"),
    refetchInterval: 60_000,
  });
}

export function useMarkRead() {
  const qc = useQueryClient();
  return useMutation<Notification, ApiError, number>({
    mutationFn: (id) =>
      api<Notification>(`/api/notifications/${id}/read/`, {
        method: "POST",
        json: {},
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  return useMutation<{ updated: number }, ApiError, void>({
    mutationFn: () =>
      api("/api/notifications/mark-all-read/", { method: "POST", json: {} }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });
}
