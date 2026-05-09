/**
 * Premium-Sidebar-Layout (Linear/Notion-Style).
 *
 * Linke Spalte (220 px): Logo + Module-Nav + User-Footer.
 * Topbar (oben): Tenant-Name + Score-Mini + Notification-Bell + User-Menu.
 * Main-Content: scrollbar.
 *
 * Dichte > Spielwiese: dichte-aktuelle Information ohne Reizüberflutung.
 */

import { NotificationBell } from "@/components/layout/notification-bell";
import { Button } from "@/components/ui/button";
import { useLogout } from "@/lib/api/auth";
import { useDashboard } from "@/lib/api/dashboard";
import { useUnreadCount } from "@/lib/api/notifications";
import { useTenantSettings } from "@/lib/api/settings";
import { useAuthStore } from "@/lib/stores/auth-store";
import { cn } from "@/lib/utils";
import {
  ChevronDown,
  FileSearch,
  Inbox,
  LayoutDashboard,
  LogOut,
  type LucideIcon,
  Settings,
  Shield,
  ShieldCheck,
  UserCircle,
  Users,
} from "lucide-react";
import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

const NAV: Array<{
  to: string;
  label: string;
  icon: LucideIcon;
  group?: "compliance" | "stamm";
}> = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, group: "compliance" },
  {
    to: "/schulungen",
    label: "Schulungen",
    icon: ShieldCheck,
    group: "compliance",
  },
  { to: "/meldungen", label: "HinSchG", icon: Inbox, group: "compliance" },
  { to: "/audit", label: "Audit-Log", icon: FileSearch, group: "compliance" },
  { to: "/mitarbeiter", label: "Mitarbeiter", icon: Users, group: "stamm" },
  { to: "/settings", label: "Einstellungen", icon: Settings, group: "stamm" },
];

const SCORE_LEVEL_BG = {
  green: "bg-emerald-500",
  yellow: "bg-amber-500",
  red: "bg-rose-500",
};

export function SidebarShell() {
  const user = useAuthStore((s) => s.user);
  const logout = useLogout();
  const dashboard = useDashboard();
  const tenant = useTenantSettings();
  const unread = useUnreadCount();
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  const score = dashboard.data?.score?.master;
  const level = dashboard.data?.score?.level ?? "green";

  return (
    <div className="flex h-screen w-full bg-slate-50">
      {/* Sidebar */}
      <aside className="flex w-56 flex-col border-r bg-white">
        <div className="flex h-14 items-center gap-2 border-b px-4">
          <Shield className="text-emerald-600" size={20} />
          <span className="text-base font-semibold tracking-tight">Vaeren</span>
        </div>

        <nav className="flex-1 space-y-6 px-3 py-4 text-sm">
          <SidebarGroup
            label="Compliance"
            items={NAV.filter((n) => n.group === "compliance")}
          />
          <SidebarGroup
            label="Verwaltung"
            items={NAV.filter((n) => n.group === "stamm")}
          />
        </nav>

        <div className="border-t p-3 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span
              className={cn("h-2 w-2 rounded-full", SCORE_LEVEL_BG[level])}
              title="EU-Hosting Helsinki"
            />
            <span>EU-Hosting Helsinki</span>
          </div>
          <div className="mt-1 flex items-center gap-2">
            <ShieldCheck size={12} className="text-emerald-600" />
            <span>Fernet-encrypted</span>
          </div>
        </div>
      </aside>

      {/* Main */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Topbar */}
        <header className="flex h-14 items-center justify-between border-b bg-white px-6">
          <div className="flex items-center gap-3">
            <span className="font-medium">
              {tenant.data?.firma_name ?? "—"}
            </span>
            {tenant.data?.pilot && (
              <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-amber-800">
                Pilot
              </span>
            )}
          </div>
          <div className="flex items-center gap-3">
            {score !== undefined && (
              <Link
                to="/"
                className="flex items-center gap-2 rounded-full border bg-slate-50 px-3 py-1 text-xs font-semibold transition hover:bg-slate-100"
                title="Compliance-Index"
              >
                <span
                  className={cn(
                    "h-2.5 w-2.5 rounded-full",
                    SCORE_LEVEL_BG[level],
                  )}
                />
                <span>{score}</span>
                <span className="text-slate-500">/ 100</span>
              </Link>
            )}
            <NotificationBell unread={unread.data?.unread ?? 0} />
            <div className="relative">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setUserMenuOpen((v) => !v)}
                className="gap-2"
              >
                <UserCircle size={18} />
                <span className="text-sm">{user?.email}</span>
                <ChevronDown size={14} />
              </Button>
              {userMenuOpen && (
                <div className="absolute right-0 top-full z-50 mt-1 w-56 rounded-md border bg-white py-1 shadow-lg">
                  <Link
                    to="/mfa-setup"
                    onClick={() => setUserMenuOpen(false)}
                    className="block px-3 py-2 text-sm hover:bg-slate-50"
                  >
                    MFA verwalten
                  </Link>
                  <Link
                    to="/settings"
                    onClick={() => setUserMenuOpen(false)}
                    className="block px-3 py-2 text-sm hover:bg-slate-50"
                  >
                    Einstellungen
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setUserMenuOpen(false);
                      logout.mutate();
                    }}
                    className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm text-rose-700 hover:bg-rose-50"
                  >
                    <LogOut size={14} /> Abmelden
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-y-auto px-6 py-6">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}

function SidebarGroup({
  label,
  items,
}: {
  label: string;
  items: typeof NAV;
}) {
  return (
    <div>
      <div className="mb-2 px-2 text-[11px] font-medium uppercase tracking-wider text-slate-400">
        {label}
      </div>
      <ul className="space-y-1">
        {items.map((it) => (
          <li key={it.to}>
            <NavLink
              to={it.to}
              end={it.to === "/"}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition",
                  isActive
                    ? "bg-emerald-50 font-medium text-emerald-900"
                    : "text-slate-700 hover:bg-slate-50",
                )
              }
            >
              <it.icon size={16} />
              {it.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </div>
  );
}
