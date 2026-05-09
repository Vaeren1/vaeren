/**
 * E2E #8: Settings — MFA-Pflicht-Toggle (nur GF darf editieren).
 */
import { expect, test } from "@playwright/test";
import { E2E_GF_EMAIL, E2E_GF_PASSWORD, loginAs } from "./helpers";

test("Settings öffnen + Tab-Navigation", async ({ page }) => {
  await loginAs(page, E2E_GF_EMAIL, E2E_GF_PASSWORD);
  await page
    .getByRole("link", { name: /Einstellungen/i })
    .first()
    .click();
  await expect(page.getByText(/Einstellungen/i).first()).toBeVisible();

  await page.getByRole("button", { name: /Sicherheit/i }).click();
  await expect(page.getByText(/MFA verpflichtend/i)).toBeVisible();

  await page.getByRole("button", { name: /Datenschutz/i }).click();
  await expect(page.getByText(/Aufbewahrungsfristen/i)).toBeVisible();
});

test("Tenant-Stammdaten-Update", async ({ page }) => {
  await loginAs(page, E2E_GF_EMAIL, E2E_GF_PASSWORD);
  await page.goto("/settings");
  const newName = `E2E Test GmbH ${Date.now()}`;
  await page.getByLabel(/Firmenname/i).fill(newName);
  await page.getByRole("button", { name: /Speichern/i }).click();
  await expect(page.getByText(/aktualisiert|gespeichert/i).first()).toBeVisible(
    { timeout: 5_000 },
  );
});
