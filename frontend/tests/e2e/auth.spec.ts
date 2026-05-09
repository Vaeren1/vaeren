/**
 * E2E #1: Login (ohne MFA-Pflicht — E2E-Tenant hat mfa_required=false).
 */
import { expect, test } from "@playwright/test";
import { E2E_GF_EMAIL, E2E_GF_PASSWORD, loginAs } from "./helpers";

test("Login → Dashboard mit Score-Donut", async ({ page }) => {
  await loginAs(page, E2E_GF_EMAIL, E2E_GF_PASSWORD);
  await expect(page.getByText(/Compliance-Cockpit/i)).toBeVisible();
  await expect(page.getByText(/Compliance-Index/i)).toBeVisible();
});

test("Falsches Passwort zeigt Fehler", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel(/E-?Mail/i).fill(E2E_GF_EMAIL);
  await page.getByLabel(/Passwort/i).fill("wrong-password");
  await page.getByRole("button", { name: /Anmelden|Login/i }).click();
  await expect(page.getByText(/falsch|nicht|Fehler/i)).toBeVisible({
    timeout: 5_000,
  });
});
