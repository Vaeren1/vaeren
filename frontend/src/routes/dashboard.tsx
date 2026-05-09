/**
 * Compliance-Cockpit-Startseite. Premium-Layout für KMU-Demo.
 *
 * Hierarchie:
 *  1. Score-Donut + KPI-Karten (Hero)
 *  2. „Diese Woche zu erledigen" (Action über Statistik)
 *  3. Modul-Status-Karten
 *  4. Activity-Feed (letzte 10 Audit-Einträge)
 */

import { ScoreDonut } from "@/components/dashboard/score-donut";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  type DashboardActivity,
  type DashboardTask,
  type ModuleScore,
  useDashboard,
} from "@/lib/api/dashboard";
import { cn } from "@/lib/utils";
import {
  AlertTriangle,
  ArrowRight,
  Calendar,
  CheckCircle2,
  Clock,
  FileSearch,
  Inbox,
  type LucideIcon,
  ShieldCheck,
} from "lucide-react";
import { Link } from "react-router-dom";

const MODULE_ICON: Record<string, LucideIcon> = {
  pflichtunterweisung: ShieldCheck,
  hinschg: Inbox,
};

const AKTION_ICON: Record<string, { icon: LucideIcon; color: string }> = {
  create: { icon: CheckCircle2, color: "text-emerald-600" },
  update: { icon: FileSearch, color: "text-sky-600" },
  delete: { icon: AlertTriangle, color: "text-rose-600" },
  login: { icon: Clock, color: "text-slate-500" },
  logout: { icon: Clock, color: "text-slate-500" },
  export: { icon: FileSearch, color: "text-purple-600" },
};

export function DashboardPage() {
  const { data, isLoading, isError } = useDashboard();

  if (isLoading) return <DashboardSkeleton />;
  if (isError || !data) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-sm text-slate-500">
          Fehler beim Laden des Dashboards.
        </CardContent>
      </Card>
    );
  }

  const {
    score,
    this_week_tasks,
    overdue_tasks,
    recent_activity,
    module_summary,
  } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">
          Compliance-Cockpit
        </h1>
        <p className="mt-1 text-sm text-slate-500">
          Ihr aktueller Compliance-Stand auf einen Blick.
        </p>
      </div>

      {/* Hero: Score + KPI-Karten */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle>Compliance-Index</CardTitle>
            <CardDescription>
              Letzte Aktualisierung: gerade eben
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center pt-2">
            <ScoreDonut score={score} />
          </CardContent>
        </Card>

        <div className="grid grid-cols-2 gap-4 lg:col-span-2">
          <KpiCard
            label="Überfällig"
            value={score.overdue_count}
            sub="Aufgaben mit verstrichener Frist"
            tone={score.overdue_count > 0 ? "red" : "green"}
            icon={AlertTriangle}
            link="/"
          />
          <KpiCard
            label="Diese Woche"
            value={score.due_in_7d_count}
            sub="Fällig in den nächsten 7 Tagen"
            tone={score.due_in_7d_count > 0 ? "yellow" : "green"}
            icon={Calendar}
          />
          <KpiCard
            label="Aktive Aufgaben"
            value={score.total_active_tasks}
            sub="Insgesamt zu bearbeiten"
            tone="neutral"
            icon={CheckCircle2}
          />
          <KpiCard
            label="Offene Meldungen"
            value={module_summary.hinschg.offene_meldungen}
            sub={`${module_summary.hinschg.neu_30d} neu in 30 Tagen`}
            tone={
              module_summary.hinschg.offene_meldungen > 0 ? "yellow" : "green"
            }
            icon={Inbox}
            link="/meldungen"
          />
        </div>
      </div>

      {/* Diese Woche zu erledigen */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Diese Woche zu erledigen</CardTitle>
            <CardDescription>
              Aufgaben mit Frist in den nächsten 7 Tagen.
            </CardDescription>
          </div>
          <span className="rounded-full bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800">
            {this_week_tasks.length} offen
          </span>
        </CardHeader>
        <CardContent>
          {overdue_tasks.length > 0 && (
            <div className="mb-4 rounded-md border border-rose-200 bg-rose-50 p-3">
              <h3 className="flex items-center gap-2 text-sm font-medium text-rose-800">
                <AlertTriangle size={14} /> {overdue_tasks.length} Aufgabe
                {overdue_tasks.length === 1 ? "" : "n"} überfällig
              </h3>
              <ul className="mt-2 space-y-1 text-sm text-rose-900">
                {overdue_tasks.slice(0, 3).map((t) => (
                  <TaskRow key={t.id} task={t} variant="overdue" />
                ))}
              </ul>
            </div>
          )}
          {this_week_tasks.length === 0 ? (
            <EmptyState
              icon={CheckCircle2}
              title="Alles im Plan."
              hint="Keine Aufgabe wird in den nächsten 7 Tagen fällig."
            />
          ) : (
            <ul className="divide-y">
              {this_week_tasks.map((t) => (
                <TaskRow key={t.id} task={t} variant="upcoming" />
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      {/* Modul-Status */}
      <div className="grid gap-4 md:grid-cols-2">
        {score.modules.map((m) => (
          <ModuleCard key={m.modul} module={m} summary={module_summary} />
        ))}
      </div>

      {/* Activity-Feed */}
      <Card>
        <CardHeader>
          <CardTitle>Letzte Aktivität</CardTitle>
          <CardDescription>
            Audit-Trail (DSGVO Art. 32 erfüllt) — vollständige Historie unter{" "}
            <Link to="/audit" className="underline">
              Audit-Log
            </Link>
            .
          </CardDescription>
        </CardHeader>
        <CardContent>
          {recent_activity.length === 0 ? (
            <EmptyState
              icon={Clock}
              title="Noch keine Aktivität."
              hint="Sobald Sie oder Ihr Team Daten ändern, erscheint hier ein Eintrag."
            />
          ) : (
            <ul className="space-y-3">
              {recent_activity.map((a) => (
                <ActivityRow key={a.id} activity={a} />
              ))}
            </ul>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function KpiCard({
  label,
  value,
  sub,
  tone,
  icon: Icon,
  link,
}: {
  label: string;
  value: number;
  sub: string;
  tone: "red" | "yellow" | "green" | "neutral";
  icon: LucideIcon;
  link?: string;
}) {
  const tones = {
    red: "bg-rose-50 text-rose-800 border-rose-200",
    yellow: "bg-amber-50 text-amber-800 border-amber-200",
    green: "bg-emerald-50 text-emerald-800 border-emerald-200",
    neutral: "bg-slate-50 text-slate-800 border-slate-200",
  };
  const content = (
    <div
      className={cn(
        "flex h-full flex-col rounded-lg border p-4 transition",
        tones[tone],
        link && "cursor-pointer hover:shadow-sm",
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wide opacity-70">
          {label}
        </span>
        <Icon size={16} className="opacity-60" />
      </div>
      <div className="mt-2 flex items-baseline gap-2">
        <span className="text-3xl font-bold tabular-nums">{value}</span>
      </div>
      <p className="mt-1 text-xs opacity-80">{sub}</p>
    </div>
  );
  if (link) return <Link to={link}>{content}</Link>;
  return content;
}

function TaskRow({
  task,
  variant,
}: {
  task: DashboardTask;
  variant: "upcoming" | "overdue";
}) {
  const moduleLink =
    task.modul === "hinschg"
      ? "/meldungen"
      : task.modul === "pflichtunterweisung"
        ? "/schulungen"
        : "/";
  return (
    <li className="flex items-center justify-between py-2 text-sm">
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <span
          className={cn(
            "h-2 w-2 shrink-0 rounded-full",
            variant === "overdue" ? "bg-rose-600" : "bg-amber-500",
          )}
        />
        <Link to={moduleLink} className="truncate font-medium hover:underline">
          {task.titel}
        </Link>
        <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-slate-600">
          {task.modul}
        </span>
      </div>
      <div className="flex items-center gap-3 text-xs text-slate-500">
        <span>{new Date(task.frist).toLocaleDateString("de-DE")}</span>
        <ArrowRight size={14} className="text-slate-400" />
      </div>
    </li>
  );
}

function ModuleCard({
  module,
  summary,
}: {
  module: ModuleScore;
  summary: {
    pflichtunterweisung: { aktive_wellen: number; abgeschlossen_30d: number };
    hinschg: { offene_meldungen: number; neu_30d: number };
  };
}) {
  const Icon = MODULE_ICON[module.modul] ?? ShieldCheck;
  const colors = {
    green: "bg-emerald-50 text-emerald-800",
    yellow: "bg-amber-50 text-amber-800",
    red: "bg-rose-50 text-rose-800",
  };
  const stats =
    module.modul === "pflichtunterweisung"
      ? [
          {
            label: "Aktive Wellen",
            value: summary.pflichtunterweisung.aktive_wellen,
          },
          {
            label: "Abgeschlossen (30 d)",
            value: summary.pflichtunterweisung.abgeschlossen_30d,
          },
        ]
      : module.modul === "hinschg"
        ? [
            {
              label: "Offene Meldungen",
              value: summary.hinschg.offene_meldungen,
            },
            { label: "Neu (30 d)", value: summary.hinschg.neu_30d },
          ]
        : [];

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between">
        <div className="flex items-center gap-3">
          <div className={cn("rounded-md p-2", colors[module.level])}>
            <Icon size={20} />
          </div>
          <div>
            <CardTitle className="text-lg">{module.label}</CardTitle>
            <CardDescription>{module.detail}</CardDescription>
          </div>
        </div>
        <div
          className={cn(
            "tabular-nums rounded-full px-2 py-0.5 text-sm font-bold",
            colors[module.level],
          )}
        >
          {module.score}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-3 text-center">
          {stats.map((s) => (
            <div key={s.label} className="rounded border bg-slate-50 p-2">
              <div className="text-2xl font-semibold tabular-nums">
                {s.value}
              </div>
              <div className="text-[11px] uppercase tracking-wide text-slate-500">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function ActivityRow({ activity }: { activity: DashboardActivity }) {
  const cfg = AKTION_ICON[activity.aktion] ?? AKTION_ICON.update;
  const Icon = cfg.icon;
  return (
    <li className="flex items-start gap-3 text-sm">
      <div className={cn("mt-0.5", cfg.color)}>
        <Icon size={16} />
      </div>
      <div className="flex-1">
        <p>
          <span className="font-medium">{activity.actor_email}</span>{" "}
          <span className="text-slate-500">
            {aktionLabel(activity.aktion)}
            {activity.target_type ? ` · ${activity.target_type}` : ""}
            {activity.target_id ? ` #${activity.target_id}` : ""}
          </span>
        </p>
        <p className="text-xs text-slate-400">
          {new Date(activity.timestamp).toLocaleString("de-DE")}
        </p>
      </div>
    </li>
  );
}

function aktionLabel(a: string): string {
  switch (a) {
    case "create":
      return "hat erstellt";
    case "update":
      return "hat aktualisiert";
    case "delete":
      return "hat gelöscht";
    case "login":
      return "hat sich angemeldet";
    case "logout":
      return "hat sich abgemeldet";
    case "export":
      return "hat exportiert";
    default:
      return a;
  }
}

function EmptyState({
  icon: Icon,
  title,
  hint,
}: {
  icon: LucideIcon;
  title: string;
  hint: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-8 text-center">
      <div className="rounded-full bg-emerald-50 p-3 text-emerald-600">
        <Icon size={24} />
      </div>
      <p className="mt-3 text-sm font-medium">{title}</p>
      <p className="mt-1 text-xs text-slate-500">{hint}</p>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="space-y-6">
      <div className="h-8 w-64 animate-pulse rounded bg-slate-200" />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="h-72 animate-pulse rounded-lg bg-slate-100" />
        <div className="grid grid-cols-2 gap-4 lg:col-span-2">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="h-28 animate-pulse rounded-lg bg-slate-100"
            />
          ))}
        </div>
      </div>
      <div className="h-48 animate-pulse rounded-lg bg-slate-100" />
    </div>
  );
}
