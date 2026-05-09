/**
 * E2E #4: Public Quiz öffnen via Token (sanity check — keine vollständige Quiz-Lösung,
 * weil das einen seeded Token braucht).
 */
import { expect, test } from "@playwright/test";

test("Public Schulungs-URL gibt 404 für unbekannten Token", async ({
  page,
}) => {
  await page.goto("/schulung/unbekannter-token-123");
  await expect(
    page.getByText(/ungültig|abgelaufen|nicht gefunden/i),
  ).toBeVisible({
    timeout: 5_000,
  });
});
