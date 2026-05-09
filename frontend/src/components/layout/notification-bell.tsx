import { Button } from "@/components/ui/button";
import {
  type Notification,
  useMarkAllRead,
  useMarkRead,
  useNotificationList,
} from "@/lib/api/notifications";
import { cn } from "@/lib/utils";
import { Bell } from "lucide-react";
import { useEffect, useRef, useState } from "react";

const TEMPLATE_LABEL: Record<string, string> = {
  hinschg_meldung_eingegangen: "Neue HinSchG-Meldung",
  compliance_task_reminder: "Erinnerung: Frist nähert sich",
  compliance_task_overdue: "Aufgabe überfällig",
};

function describe(n: Notification): string {
  const label = TEMPLATE_LABEL[n.template] ?? n.template;
  const ctx = n.template_kontext as Record<string, unknown>;
  if (n.template === "compliance_task_reminder") {
    return `${label}: "${ctx.titel}" in ${ctx.tage_bis_frist} Tagen`;
  }
  if (n.template === "compliance_task_overdue") {
    return `${label}: "${ctx.titel}" seit ${ctx.tage_ueberfaellig} Tagen`;
  }
  if (n.template === "hinschg_meldung_eingegangen") {
    return `${label} (${ctx.token_short}…)`;
  }
  return label;
}

export function NotificationBell({ unread }: { unread: number }) {
  const [open, setOpen] = useState(false);
  const popRef = useRef<HTMLDivElement>(null);
  const list = useNotificationList(open);
  const markRead = useMarkRead();
  const markAllRead = useMarkAllRead();

  useEffect(() => {
    function onClick(e: MouseEvent) {
      if (popRef.current && !popRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div className="relative" ref={popRef}>
      <Button
        variant="ghost"
        size="sm"
        onClick={() => setOpen((v) => !v)}
        className="relative"
        aria-label="Benachrichtigungen"
      >
        <Bell size={18} />
        {unread > 0 && (
          <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-600 px-1 text-[10px] font-bold text-white">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </Button>
      {open && (
        <div className="absolute right-0 top-full z-50 mt-1 w-80 rounded-md border bg-white shadow-lg">
          <div className="flex items-center justify-between border-b px-3 py-2">
            <span className="text-sm font-medium">Benachrichtigungen</span>
            {unread > 0 && (
              <button
                type="button"
                className="text-xs text-emerald-700 hover:underline"
                onClick={() => markAllRead.mutate()}
              >
                Alle gelesen markieren
              </button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {list.isLoading && (
              <div className="space-y-2 p-3">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-10 animate-pulse rounded bg-slate-100"
                  />
                ))}
              </div>
            )}
            {list.data && list.data.length === 0 && (
              <p className="p-6 text-center text-sm text-slate-500">
                Keine Benachrichtigungen.
              </p>
            )}
            {list.data?.map((n) => {
              const isUnread = n.status !== "geoeffnet";
              return (
                <button
                  type="button"
                  key={n.id}
                  className={cn(
                    "block w-full border-b p-3 text-left text-sm transition hover:bg-slate-50",
                    isUnread && "bg-emerald-50/50",
                  )}
                  onClick={() => {
                    if (isUnread) markRead.mutate(n.id);
                  }}
                >
                  <div className="flex items-start gap-2">
                    {isUnread && (
                      <span className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-emerald-600" />
                    )}
                    <div className="flex-1">
                      <p className="leading-snug">{describe(n)}</p>
                      <p className="mt-0.5 text-xs text-slate-500">
                        {new Date(n.created_at).toLocaleString("de-DE", {
                          dateStyle: "short",
                          timeStyle: "short",
                        })}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
