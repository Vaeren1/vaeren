/**
 * E2E #6: HinSchG-Bearbeiter (Compliance-Beauftragte:r) öffnet Meldung
 * und klassifiziert sie (Kategorie/Schweregrad/Status).
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

test("Klassifizierung — Kategorie/Schweregrad/Status sind editierbar und persistieren", async ({
  page,
}) => {
  // Public-Submission, dann CB-Login, dann in die Detail-Ansicht
  const titel = `Klassifizierung-${Date.now()}`;
  await page.goto("/hinweise");
  await page.getByLabel(/Kurztitel/i).fill(titel);
  await page.getByLabel(/Beschreibung/i).fill("Test Klassifizierungs-Bug.");
  await page.getByRole("button", { name: /Meldung absenden/i }).click();
  await expect(page.getByText(/erfolgreich übermittelt/i)).toBeVisible({
    timeout: 5_000,
  });

  await loginAs(page, E2E_CB_EMAIL, E2E_CB_PASSWORD);
  await page
    .getByRole("link", { name: /HinSchG/i })
    .first()
    .click();
  await page.getByRole("link", { name: titel }).click();

  // --- Bug-Reproducer: ohne Fix konnte man hier nichts ins Kategorie-Feld tippen.
  const kategorieInput = page.getByLabel(/Kategorie/i);
  await kategorieInput.fill("Korruption");
  await expect(kategorieInput).toHaveValue("Korruption");
  // onBlur commited den PATCH
  await kategorieInput.blur();

  // Selects feuern PATCH sofort bei onChange
  await page.getByLabel(/Schweregrad/i).selectOption("hoch");
  await page.getByLabel(/^Status$/i).selectOption("in_pruefung");

  // Page-Reload — Werte müssen persistiert sein
  await page.reload();
  await expect(page.getByLabel(/Kategorie/i)).toHaveValue("Korruption");
  await expect(page.getByLabel(/Schweregrad/i)).toHaveValue("hoch");
  await expect(page.getByLabel(/^Status$/i)).toHaveValue("in_pruefung");
});
