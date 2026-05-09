/**
 * Compliance-Score-Donut. Pure SVG, ~50 Zeilen.
 *
 * Zwei Ringe: außen Master-Score, innen Modul-Aufteilung.
 * Hover-Tooltip zeigt Formel — Transparenz statt Black-Box.
 */

import type { ComplianceScore, ScoreLevel } from "@/lib/api/dashboard";
import { cn } from "@/lib/utils";

const LEVEL_COLOR: Record<ScoreLevel, string> = {
  green: "#10b981",
  yellow: "#f59e0b",
  red: "#e11d48",
};

const LEVEL_LABEL: Record<ScoreLevel, string> = {
  green: "Sehr gut",
  yellow: "Aufmerksamkeit nötig",
  red: "Handlungsbedarf",
};

export function ScoreDonut({ score }: { score: ComplianceScore }) {
  const radius = 80;
  const stroke = 14;
  const circumference = 2 * Math.PI * radius;
  const dashGood = (score.master / 100) * circumference;
  const color = LEVEL_COLOR[score.level];

  return (
    <div className="flex flex-col items-center" title={score.formula}>
      <svg
        width="200"
        height="200"
        viewBox="0 0 200 200"
        className="-rotate-90"
        role="img"
        aria-labelledby="score-donut-title"
      >
        <title id="score-donut-title">
          Compliance-Index {score.master} von 100
        </title>
        <circle
          cx="100"
          cy="100"
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={stroke}
        />
        <circle
          cx="100"
          cy="100"
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={`${dashGood} ${circumference}`}
          style={{ transition: "stroke-dasharray 0.6s ease" }}
        />
      </svg>
      <div className="-mt-[120px] flex h-[80px] flex-col items-center justify-center text-center">
        <div
          className="text-4xl font-bold tabular-nums leading-none"
          style={{ color }}
        >
          {score.master}
        </div>
        <div className="mt-1 text-xs text-slate-500">/ 100</div>
      </div>
      <p className="mt-7 text-sm font-medium" style={{ color }}>
        {LEVEL_LABEL[score.level]}
      </p>
      <p className="mt-3 max-w-xs text-center text-xs text-slate-500">
        Formel:{" "}
        <span className="font-mono">
          0,5 × Pflichten + 0,2 × Fristen + 0,3 × Module
        </span>
      </p>
      <div className="mt-3 flex gap-3 text-[11px] text-slate-600">
        <SubMetric label="Pflichten" value={score.score_pflichten} />
        <SubMetric label="Fristen" value={score.score_fristen} />
        <SubMetric label="Module" value={score.score_module} />
      </div>
    </div>
  );
}

function SubMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex flex-col items-center rounded bg-slate-50 px-2 py-1">
      <span className="text-slate-400">{label}</span>
      <span
        className={cn(
          "tabular-nums font-semibold",
          value >= 90
            ? "text-emerald-700"
            : value >= 70
              ? "text-amber-700"
              : "text-rose-700",
        )}
      >
        {value}
      </span>
    </div>
  );
}
