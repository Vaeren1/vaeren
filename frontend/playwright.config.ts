import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright config — 8 kritische User-Journeys (Sprint 7).
 *
 * Spec §10: „sparsam, nur main". CI-Job läuft mit `if: github.ref == 'refs/heads/main'`.
 * Lokal: Backend muss separat laufen (`uv run python manage.py runserver`).
 * In CI: webServer wird automatisch gestartet.
 */

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://dev.app.vaeren.local:5173";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  reporter: process.env.CI ? [["github"], ["html", { open: "never" }]] : "list",
  timeout: 30_000,
  expect: { timeout: 5_000 },
  use: {
    baseURL,
    trace: "retain-on-failure",
    video: "retain-on-failure",
    locale: "de-DE",
    timezoneId: "Europe/Berlin",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
