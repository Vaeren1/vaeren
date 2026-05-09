/**
 * E2E #5: HinSchG anonyme Submission + Status-Page.
 */
import { expect, test } from "@playwright/test";

test("Anonyme HinSchG-Meldung anlegen + Token-Status öffnen", async ({
  page,
}) => {
  await page.goto("/hinweise");
  await expect(page.getByText(/Hinweis melden/i)).toBeVisible();
  await page.getByLabel(/Kurztitel/i).fill("E2E Verdacht");
  await page.getByLabel(/Beschreibung/i).fill("Beobachtung am E2E-Tag.");
  await page.getByRole("button", { name: /Meldung absenden/i }).click();

  // Token wird angezeigt — wir kopieren ihn aus dem Status-Link
  const statusLink = page.getByRole("link", {
    name: /\/hinweise\/status\//,
  });
  await expect(statusLink).toBeVisible({ timeout: 5_000 });
  const href = await statusLink.getAttribute("href");
  expect(href).toBeTruthy();

  await page.goto(href ?? "");
  await expect(page.getByText(/Status Ihrer Meldung/i)).toBeVisible();
  await expect(page.getByText(/Eingegangen/i)).toBeVisible();
});
