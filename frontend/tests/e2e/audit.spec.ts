/**
 * E2E #7: Audit-Log + CSV-Export.
 */
import { expect, test } from "@playwright/test";
import { E2E_GF_EMAIL, E2E_GF_PASSWORD, loginAs } from "./helpers";

test("Audit-Log lädt + CSV-Download verfügbar", async ({ page }) => {
  await loginAs(page, E2E_GF_EMAIL, E2E_GF_PASSWORD);
  await page
    .getByRole("link", { name: /Audit-Log/i })
    .first()
    .click();
  await expect(page.getByText(/Audit-Log/i).first()).toBeVisible();

  const csvLink = page.getByRole("link", { name: /CSV exportieren/i });
  await expect(csvLink).toBeVisible();
  await expect(csvLink).toHaveAttribute("href", /\/api\/audit\/export\.csv/);
});

test("Audit-Filter per Aktion", async ({ page }) => {
  await loginAs(page, E2E_GF_EMAIL, E2E_GF_PASSWORD);
  await page.goto("/audit");
  await page.locator("select").first().selectOption({ value: "create" });
  // Tabelle re-rendert — wir prüfen nicht die Inhalte, weil Audit-Daten
  // dynamisch sind, sondern dass kein Fehler auftaucht.
  await expect(page.getByText(/Aktor/i)).toBeVisible();
});
