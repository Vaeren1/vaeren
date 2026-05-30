/**
 * Radar-Variante C — Vorher/Nachher-Split (§11).
 *
 * Links die roten Lücken (Status heute), rechts der grüne Soll-Zustand nach
 * Aktivierung der empfohlenen Module. Verdeutlicht den Mehrwert der
 * Aktivierung visuell als Kontrast.
 */
import { Button } from "@/components/ui/button";
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

export function RadarVarianteC({
  radar,
  firmenname,
  kanzleiName,
  onNext,
}: RadarProps) {
  const kiPending = kiPendingEmpfehlungen(radar.empfehlungen);
  const abgedeckt = radar.befunde.filter((b) => b.abdeckung === "voll_modul");

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

      <div className="grid gap-4 md:grid-cols-2">
        {/* Vorher: offene Lücken */}
        <div className="rounded-lg border border-rose-200 bg-rose-50 p-4">
          <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-rose-800">
            <span aria-hidden>⚠️</span> Heute: offene Pflichten
          </p>
          <ul className="space-y-2">
            {radar.befunde.map((b) => (
              <li
                key={b.regulierung_code}
                className="rounded border border-rose-200 bg-white/70 px-3 py-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium text-rose-900">{b.name}</p>
                  <RelevanzChip relevanz={b.relevanz} />
                </div>
                <p className="text-xs text-rose-700">noch nicht abgedeckt</p>
              </li>
            ))}
          </ul>
        </div>

        {/* Nachher: nach Aktivierung */}
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <p className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-800">
            <span aria-hidden>✅</span> Nach Aktivierung
          </p>
          <ul className="space-y-2">
            {radar.befunde.map((b) => {
              const meta = abdeckungMeta(b.abdeckung);
              const empf = empfehlungenFuerBefund(b, radar.empfehlungen);
              return (
                <li
                  key={b.regulierung_code}
                  className={`rounded border bg-white/70 px-3 py-2 ${meta.ring}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium">{b.name}</p>
                    <StatusBadge abdeckung={b.abdeckung} />
                  </div>
                  <EmpfehlungListe empfehlungen={empf} />
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      <p className="text-center text-sm text-muted-foreground">
        {abgedeckt.length} von {radar.befunde.length} Pflichten lassen sich
        direkt mit einem Vaeren-Modul abdecken.
      </p>

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
