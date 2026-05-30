/**
 * RadarScreen — der im Wizard gerenderte Compliance-Radar (Schritt 4).
 *
 * Rendert vorerst Variante A (animierter Scan) als Default. Die Varianten
 * B/C sind über `RadarScreen.stories.tsx` vergleichbar; die finale Auswahl
 * trifft ein Mensch (Konrad) im Storybook und tauscht hier ggf. die
 * importierte Komponente aus.
 */
import { RadarVarianteA } from "./RadarVarianteA";
import type { RadarProps } from "./radar-shared";

export function RadarScreen(props: RadarProps) {
  return <RadarVarianteA {...props} />;
}
