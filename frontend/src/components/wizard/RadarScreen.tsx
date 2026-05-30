/**
 * RadarScreen — der im Wizard gerenderte Compliance-Radar (Schritt 4).
 *
 * Variante A (animierter Scan) wurde 2026-05-30 als finale UI-Variante
 * gewählt (Spec §11). Die Explorations-Varianten B/C wurden danach entfernt.
 */
import { RadarVarianteA } from "./RadarVarianteA";
import type { RadarProps } from "./radar-shared";

export function RadarScreen(props: RadarProps) {
  return <RadarVarianteA {...props} />;
}
