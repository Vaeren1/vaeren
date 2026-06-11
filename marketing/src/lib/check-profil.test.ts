import { describe, expect, test } from "bun:test";
import { decodeProfil, encodeProfil, zuProfilData, type CheckAntworten } from "./check-profil";

const antworten: CheckAntworten = {
  branche: "metall", ma: 150, umsatz: 25_000_000, rechtsform: "gmbh",
  flags: { stellt_produkte_her: true, produkte_mit_digitalen_elementen: false, setzt_ki_ein: true, hat_oem_kunden: true },
  daten: { verarbeitet_personenbezogene_daten: true, verarbeitet_gesundheits_sozialdaten: false },
};

describe("check-profil encode/decode", () => {
  test("roundtrip", () => {
    expect(decodeProfil(encodeProfil(antworten))).toEqual(antworten);
  });

  test("decode von kaputtem Input liefert null", () => {
    expect(decodeProfil("unsinn")).toBeNull();
    expect(decodeProfil("")).toBeNull();
    expect(decodeProfil("nichtdabei.x.y.z.q")).toBeNull();
  });

  test("zuProfilData setzt Sektor und Automotive-Flag aus der Branche", () => {
    const p = zuProfilData({ ...antworten, branche: "automotive" });
    expect(p.nis2_sektor).toBe("industrie");
    expect(p.ist_automotive_zulieferer).toBe(true);
    expect(p.mitarbeiter_anzahl).toBe(150);
    expect(p.jahresumsatz_eur).toBe(25_000_000);
  });

  test("Rechtsform-Key mit Punkt-Label (GmbH & Co. KG) übersteht den Roundtrip", () => {
    const a = { ...antworten, rechtsform: "gmbh_co_kg" };
    expect(decodeProfil(encodeProfil(a))).toEqual(a);
    expect(zuProfilData(a).rechtsform).toBe("gmbh & co. kg");
  });
});
