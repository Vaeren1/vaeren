import type { LucideIcon } from "lucide-react";

export interface EmptyStateProps {
  icon: LucideIcon;
  title: string;
  hint: string;
  tone?: "success" | "neutral";
  action?: React.ReactNode;
}

export function EmptyState({
  icon: Icon,
  title,
  hint,
  tone = "neutral",
  action,
}: EmptyStateProps) {
  const toneCls =
    tone === "success"
      ? "bg-emerald-50 text-emerald-600"
      : "bg-slate-100 text-slate-500";
  return (
    <div className="flex flex-col items-center justify-center py-10 text-center">
      <div className={`rounded-full p-3 ${toneCls}`}>
        <Icon size={24} />
      </div>
      <p className="mt-3 text-sm font-medium">{title}</p>
      <p className="mt-1 max-w-md text-xs text-slate-500">{hint}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
