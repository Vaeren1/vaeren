import { describe, expect, test } from "bun:test";
import { bewerteRegulierungen, KATALOG, type ProfilData } from "./relevanz";
import fixtures from "./relevanz-testvektoren.json";

// Parität TS-Port ↔ backend/core/regulierungen.py. Bei FAIL: immer den
// TS-Port korrigieren, nie die Fixture (die kommt aus dem Python-Katalog).
describe("relevanz.ts ↔ core/regulierungen.py Parität", () => {
  test("Katalog-Codes identisch", () => {
    expect(KATALOG.map(r => r.code).sort()).toEqual(fixtures.katalog_codes);
  });

  for (const [i, v] of fixtures.vektoren.entries()) {
    test(`Vektor ${i}: ${JSON.stringify(v.profil).slice(0, 80)}`, () => {
      const codes = bewerteRegulierungen(v.profil as ProfilData).map(b => b.code).sort();
      expect(codes).toEqual(v.erwartete_codes);
    });
  }
});
