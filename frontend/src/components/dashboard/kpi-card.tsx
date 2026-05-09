import { cn } from "@/lib/utils";
import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

export type KpiTone = "red" | "yellow" | "green" | "neutral";

export interface KpiCardProps {
  label: string;
  value: number;
  sub: string;
  tone: KpiTone;
  icon: LucideIcon;
  link?: string;
}

const TONES: Record<KpiTone, string> = {
  red: "bg-rose-50 text-rose-800 border-rose-200",
  yellow: "bg-amber-50 text-amber-800 border-amber-200",
  green: "bg-emerald-50 text-emerald-800 border-emerald-200",
  neutral: "bg-slate-50 text-slate-800 border-slate-200",
};

export function KpiCard({
  label,
  value,
  sub,
  tone,
  icon: Icon,
  link,
}: KpiCardProps) {
  const content = (
    <div
      className={cn(
        "flex h-full flex-col rounded-lg border p-4 transition",
        TONES[tone],
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
