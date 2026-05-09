import { describe, expect, test } from "bun:test";
import { demoSchema } from "@/routes/demo";
import { loginSchema } from "@/routes/login";
import { mitarbeiterSchema } from "@/routes/mitarbeiter-form";

describe("loginSchema", () => {
  test("accepts valid email + 8+ char password", () => {
    const r = loginSchema.safeParse({
      email: "konrad@vaeren.de",
      password: "geheim12",
    });
    expect(r.success).toBe(true);
  });

  test("rejects invalid email", () => {
    const r = loginSchema.safeParse({
      email: "kein-email",
      password: "geheim12",
    });
    expect(r.success).toBe(false);
  });

  test("rejects too-short password", () => {
    const r = loginSchema.safeParse({
      email: "konrad@vaeren.de",
      password: "short",
    });
    expect(r.success).toBe(false);
  });
});

describe("mitarbeiterSchema", () => {
  test("requires all key fields", () => {
    const r = mitarbeiterSchema.safeParse({
      vorname: "Anna",
      nachname: "Müller",
      email: "anna@acme.de",
      abteilung: "Produktion",
      aktiv: true,
    });
    expect(r.success).toBe(true);
  });

  test("rejects empty vorname", () => {
    const r = mitarbeiterSchema.safeParse({
      vorname: "",
      nachname: "Müller",
      email: "anna@acme.de",
      abteilung: "X",
      aktiv: true,
    });
    expect(r.success).toBe(false);
  });
});

describe("demoSchema", () => {
  test("accepts minimal valid input", () => {
    const r = demoSchema.safeParse({
      firma: "ACME",
      vorname: "A",
      nachname: "B",
      email: "a@b.de",
    });
    expect(r.success).toBe(true);
  });

  test("rejects nachricht > 2000 chars", () => {
    const r = demoSchema.safeParse({
      firma: "ACME",
      vorname: "A",
      nachname: "B",
      email: "a@b.de",
      nachricht: "x".repeat(2001),
    });
    expect(r.success).toBe(false);
  });
});
