/**
 * E2E #6: HinSchG-Bearbeiter (Compliance-Beauftragte:r) öffnet Meldung.
 */
import { expect, test } from "@playwright/test";
import { E2E_CB_EMAIL, E2E_CB_PASSWORD, loginAs } from "./helpers";

test("Compliance-Beauftragte:r sieht HinSchG-Liste", async ({ page }) => {
  // Erst Public-Submission, damit eine Meldung existiert
  await page.goto("/hinweise");
  await page.getByLabel(/Kurztitel/i).fill("E2E Bearbeiter-Test");
  await page.getByLabel(/Beschreibung/i).fill("Bearbeiter-Spec.");
  await page.getByRole("button", { name: /Meldung absenden/i }).click();
  await expect(page.getByText(/erfolgreich übermittelt/i)).toBeVisible({
    timeout: 5_000,
  });

  // Dann als CB einloggen
  await loginAs(page, E2E_CB_EMAIL, E2E_CB_PASSWORD);
  await page
    .getByRole("link", { name: /HinSchG/i })
    .first()
    .click();
  await expect(page.getByText(/HinSchG-Meldungen/i)).toBeVisible();
});
