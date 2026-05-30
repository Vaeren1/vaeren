/**
 * Radar-Variante B — Karten-Reveal (§11).
 *
 * Pflicht-Karten klappen nacheinander auf (gestaffeltes Fade-in), farb-
 * codiert grün/gelb/grau über den Abdeckungs-Gradient.
 */
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import {
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

export function RadarVarianteB({
  radar,
  firmenname,
  kanzleiName,
  onNext,
}: RadarProps) {
  const [sichtbar, setSichtbar] = useState(0);

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
    }, 250);
    return () => clearInterval(id);
  }, [radar.befunde.length]);

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

      <div className="grid gap-3 sm:grid-cols-2">
        {radar.befunde.map((b, i) => {
          const meta = abdeckungMeta(b.abdeckung);
          const istSichtbar = i < sichtbar;
          const empf = empfehlungenFuerBefund(b, radar.empfehlungen);
          return (
            <div
              key={b.regulierung_code}
              className={`rounded-lg border p-4 transition-all duration-500 ${meta.ring} ${
                istSichtbar ? "scale-100 opacity-100" : "scale-95 opacity-0"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-2xl" aria-hidden>
                  {meta.icon}
                </span>
                <StatusBadge abdeckung={b.abdeckung} />
              </div>
              <p className="mt-2 font-medium">{b.name}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">
                {b.begruendung}
              </p>
              <div className="mt-2">
                <RelevanzChip relevanz={b.relevanz} />
              </div>
              <EmpfehlungListe empfehlungen={empf} />
            </div>
          );
        })}
      </div>

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
    </div>
  );
}
