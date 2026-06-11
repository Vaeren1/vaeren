// Schießt Produkt-Screenshots vom Demo-Tenant für die Marketing-Site
// (Produktbeweis-Sektion auf der Startseite).
//
// Aufruf (lokal, NICHT auf dem Server):
//   cd marketing
//   VAEREN_DEMO_USER=… VAEREN_DEMO_PASS=… bun run screenshots
//
// Ablage: src/assets/screenshots/*.png — werden committet, der statische
// Build braucht sie zur Build-Zeit. Bricht ein Screenshot weg (Route geändert,
// MFA aktiv), wird er übersprungen; die Sektion blendet fehlende Bilder
// automatisch aus.
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";

const BASE = process.env.VAEREN_DEMO_BASE ?? "https://app.vaeren.de";
const USER = process.env.VAEREN_DEMO_USER;
const PASS = process.env.VAEREN_DEMO_PASS;
if (!USER || !PASS) {
  console.error("VAEREN_DEMO_USER / VAEREN_DEMO_PASS fehlen");
  process.exit(1);
}

// Routen aus frontend/src/router.tsx — bei Router-Änderungen hier nachziehen.
const SHOTS = [
  { pfad: "/", datei: "cockpit.png", warteAuf: "text=Compliance" },
  { pfad: "/onboarding-wizard", datei: "wizard.png", warteAuf: "text=Willkommen" },
  { pfad: "/fragebogen", datei: "fragebogen.png", warteAuf: "text=Fragebogen" },
];

mkdirSync("src/assets/screenshots", { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });

await page.goto(`${BASE}/login`);
await page.fill("#email", USER);
await page.fill("#password", PASS);
await page.click('button[type="submit"]');
await page.waitForLoadState("networkidle");

if (page.url().includes("mfa-challenge")) {
  console.error("Demo-Konto verlangt MFA — Screenshots übersprungen. Konto ohne TOTP verwenden.");
  await browser.close();
  process.exit(2);
}

let ok = 0;
for (const s of SHOTS) {
  try {
    await page.goto(`${BASE}${s.pfad}`);
    await page.waitForSelector(s.warteAuf, { timeout: 15000 });
    await page.waitForTimeout(800); // Charts/Animationen ausrendern lassen
    await page.screenshot({ path: `src/assets/screenshots/${s.datei}` });
    console.log(`✓ ${s.datei}`);
    ok++;
  } catch (e) {
    console.warn(`✗ ${s.datei}: ${e.message.split("\n")[0]} — übersprungen`);
  }
}
await browser.close();
console.log(`${ok}/${SHOTS.length} Screenshots aktualisiert.`);
