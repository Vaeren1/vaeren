/**
 * E2E #2: Mitarbeiter erstellen + bearbeiten.
 */
import { expect, test } from "@playwright/test";
import { E2E_GF_EMAIL, E2E_GF_PASSWORD, loginAs } from "./helpers";

test("Mitarbeiter:in anlegen", async ({ page }) => {
  await loginAs(page, E2E_GF_EMAIL, E2E_GF_PASSWORD);
  await page
    .getByRole("link", { name: /Mitarbeiter/i })
    .first()
    .click();
  await page
    .getByRole("link", { name: /\+ Neue|Neu|anlegen/i })
    .first()
    .click();
  const random = `Test${Date.now()}`;
  await page.getByLabel(/Vorname/i).fill("Max");
  await page.getByLabel(/Nachname/i).fill(random);
  await page.getByLabel(/E-?Mail/i).fill(`${random.toLowerCase()}@e2e.de`);
  await page.getByLabel(/Abteilung/i).fill("Vertrieb");
  await page.getByLabel(/Rolle|Position/i).fill("Vertriebsmitarbeiter");
  await page.getByLabel(/Eintritt/i).fill("2025-01-15");
  await page.getByRole("button", { name: /Speichern|Anlegen/i }).click();
  await expect(page.getByText(random)).toBeVisible({ timeout: 5_000 });
});
