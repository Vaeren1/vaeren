import { describe, expect, test } from "bun:test";
import { AXES, FIRMS } from "./teaser-firmen";

describe("teaser-firmen", () => {
  test("vals entsprechen den Modul-Listen je Kategorie", () => {
    for (const f of FIRMS) {
      AXES.forEach((achse, i) => {
        const anzahl = (f.module[achse] ?? []).length;
        expect({ firma: f.name, achse, anzahl }).toEqual({ firma: f.name, achse, anzahl: f.vals[i] });
      });
    }
  });

  test("maximale Pflichtenzahl ist 12 (Tabellenhöhe)", () => {
    for (const f of FIRMS) {
      expect(f.vals.reduce((a, b) => a + b, 0)).toBeLessThanOrEqual(12);
    }
  });
});
