// Kompakte URL-Kodierung des Schnell-Check-Profils für Deep-Links:
//   ?p=<branche>.<ma>.<umsatzMio>.<rechtsform>.<flagsHex>
// Bits: 1 produkte, 2 digital, 4 ki, 8 oem, 16 persDaten, 32 gesundheitsdaten.
// Reist als Klartext-Parameter (kein Tracking, keine Speicherung vor Absenden).
import { BRANCHE_BY_KEY } from "../data/branchen";
import { LEERES_PROFIL, type ProfilData } from "./relevanz";

export interface CheckAntworten {
  branche: string;
  ma: number;
  umsatz: number;
  rechtsform: string;
  flags: { stellt_produkte_her: boolean; produkte_mit_digitalen_elementen: boolean; setzt_ki_ein: boolean; hat_oem_kunden: boolean };
  daten: { verarbeitet_personenbezogene_daten: boolean; verarbeitet_gesundheits_sozialdaten: boolean };
}

export function encodeProfil(a: CheckAntworten): string {
  const bits = (a.flags.stellt_produkte_her ? 1 : 0) | (a.flags.produkte_mit_digitalen_elementen ? 2 : 0)
    | (a.flags.setzt_ki_ein ? 4 : 0) | (a.flags.hat_oem_kunden ? 8 : 0)
    | (a.daten.verarbeitet_personenbezogene_daten ? 16 : 0) | (a.daten.verarbeitet_gesundheits_sozialdaten ? 32 : 0);
  return [a.branche, a.ma, a.umsatz / 1_000_000, a.rechtsform || "-", bits.toString(16)].join(".");
}

export function decodeProfil(p: string): CheckAntworten | null {
  const teile = (p || "").split(".");
  if (teile.length !== 5) return null;
  const [branche, maStr, umsatzStr, rechtsformRaw, bitsStr] = teile;
  if (!BRANCHE_BY_KEY.has(branche)) return null;
  const ma = Number(maStr);
  const umsatzMio = Number(umsatzStr);
  const bits = parseInt(bitsStr, 16);
  if (!Number.isFinite(ma) || !Number.isFinite(umsatzMio) || Number.isNaN(bits)) return null;
  return {
    branche, ma, umsatz: umsatzMio * 1_000_000, rechtsform: rechtsformRaw === "-" ? "" : rechtsformRaw,
    flags: {
      stellt_produkte_her: !!(bits & 1), produkte_mit_digitalen_elementen: !!(bits & 2),
      setzt_ki_ein: !!(bits & 4), hat_oem_kunden: !!(bits & 8),
    },
    daten: { verarbeitet_personenbezogene_daten: !!(bits & 16), verarbeitet_gesundheits_sozialdaten: !!(bits & 32) },
  };
}

export function zuProfilData(a: CheckAntworten): ProfilData {
  const branche = BRANCHE_BY_KEY.get(a.branche);
  return {
    ...LEERES_PROFIL,
    mitarbeiter_anzahl: a.ma,
    jahresumsatz_eur: a.umsatz,
    rechtsform: a.rechtsform,
    nis2_sektor: branche?.sektor ?? "sonstiges",
    ist_automotive_zulieferer: branche?.defaults?.ist_automotive_zulieferer ?? false,
    ...a.flags,
    ...a.daten,
  };
}
