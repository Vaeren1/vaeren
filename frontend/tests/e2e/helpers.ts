import { type Page, expect } from "@playwright/test";

export const E2E_GF_EMAIL = "gf@e2e.de";
export const E2E_GF_PASSWORD = "E2E-test-1234!";
export const E2E_CB_EMAIL = "compl@e2e.de";
export const E2E_CB_PASSWORD = "E2E-test-1234!";

export async function loginAs(
  page: Page,
  email: string,
  password: string,
): Promise<void> {
  await page.goto("/login");
  await page.getByLabel(/E-?Mail/i).fill(email);
  await page.getByLabel(/Passwort/i).fill(password);
  await page.getByRole("button", { name: /Anmelden|Login/i }).click();
  // Nach erfolgreichem Login: Sidebar mit „Vaeren"-Logo sichtbar
  await expect(page.getByRole("link", { name: /Vaeren/ })).toBeVisible({
    timeout: 10_000,
  });
}
