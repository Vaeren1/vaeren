/**
 * Radar-Variante A — Animierter Scan (§11).
 *
 * Ein Radar-Sweep läuft, Pflichten erscheinen progressiv, der Score zählt
 * hoch. Inszenierung über CSS-Transitions + Timer; bei `reduce-motion` bzw.
 * fehlenden Pflichten degradiert sie zu einer statischen Liste.
 */
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import {
  BasisHinweisExpander,
  EmpfehlungListe,
  FirmenHeader,
  KanzleiSiegel,
  type RadarProps,
  RdgDisclaimer,
  RelevanzChip,
  StatusBadge,
  abdeckungMeta,
  empfehlungenFuerBefund,
  kiPendingEmpfehlungen,
} from "./radar-shared";

export function RadarVarianteA({
  radar,
  firmenname,
  kanzleiName,
  onNext,
}: RadarProps) {
  const [sichtbar, setSichtbar] = useState(0);
  const [score, setScore] = useState(0);
  const zielScore = Math.min(100, 40 + radar.befunde.length * 5);

  useEffect(() => {
    setSichtbar(0);
    const id = setInterval(() => {
      setSichtbar((n) => {
        if (n >= radar.befunde.length) {
          clearInterval(id);
          return n;
        }
        return n + 1;
      });
    }, 350);
    return () => clearInterval(id);
  }, [radar.befunde.length]);

  useEffect(() => {
    if (sichtbar < radar.befunde.length) return;
    let cur = 0;
    const id = setInterval(() => {
      cur += 4;
      if (cur >= zielScore) {
        cur = zielScore;
        clearInterval(id);
      }
      setScore(cur);
    }, 30);
    return () => clearInterval(id);
  }, [sichtbar, radar.befunde.length, zielScore]);

  const kiPending = kiPendingEmpfehlungen(radar.empfehlungen);

  return (
    <div className="space-y-5">
      <div className="flex items-start justify-between gap-4">
        <FirmenHeader
          firmenname={firmenname}
          anzahlPflichten={radar.befunde.length}
        />
        <KanzleiSiegel name={kanzleiName} />
      </div>
      <RdgDisclaimer />

      <div className="flex items-center gap-6 rounded-lg border bg-card p-5">
        <div className="relative grid h-28 w-28 shrink-0 place-items-center overflow-hidden rounded-full border-2 border-emerald-200 bg-emerald-50">
          <div className="radar-sweep absolute inset-0" aria-hidden />
          <span className="relative text-2xl font-bold text-emerald-700">
            {score}
          </span>
        </div>
        <div>
          <p className="text-sm font-medium">Compliance-Scan läuft …</p>
          <p className="text-sm text-muted-foreground">
            {sichtbar} von {radar.befunde.length} Pflichten erfasst
          </p>
        </div>
      </div>

      <ul className="space-y-3">
        {radar.befunde.map((b, i) => {
          const meta = abdeckungMeta(b.abdeckung);
          const istSichtbar = i < sichtbar;
          const empf = empfehlungenFuerBefund(b, radar.empfehlungen);
          return (
            <li
              key={b.regulierung_code}
              className={`rounded-lg border p-4 transition-all duration-500 ${meta.ring} ${
                istSichtbar
                  ? "translate-y-0 opacity-100"
                  : "translate-y-2 opacity-0"
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <p className="font-medium">{b.name}</p>
                  <p className="mt-0.5 text-sm text-muted-foreground">
                    {b.begruendung}
                  </p>
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <StatusBadge abdeckung={b.abdeckung} />
                  <RelevanzChip relevanz={b.relevanz} />
                </div>
              </div>
              <EmpfehlungListe empfehlungen={empf} />
              <BasisHinweisExpander befund={b} />
            </li>
          );
        })}
      </ul>

      {kiPending.length > 0 && (
        <div className="rounded-lg border border-violet-200 bg-violet-50 p-4">
          <p className="text-sm font-medium text-violet-900">
            Spezielle Hinweise aus Ihren Freitext-Angaben
          </p>
          <EmpfehlungListe empfehlungen={kiPending} kiPending />
        </div>
      )}

      {onNext && (
        <div className="flex justify-end">
          <Button onClick={onNext}>Module aktivieren</Button>
        </div>
      )}

      <style>{`
        .radar-sweep {
          background: conic-gradient(
            from 0deg,
            rgba(16, 185, 129, 0.35) 0deg,
            transparent 60deg,
            transparent 360deg
          );
          animation: radar-spin 2s linear infinite;
        }
        @keyframes radar-spin {
          to { transform: rotate(360deg); }
        }
        @media (prefers-reduced-motion: reduce) {
          .radar-sweep { animation: none; }
        }
      `}</style>
    </div>
  );
}
