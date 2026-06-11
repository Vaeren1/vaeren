// Gemeinsame Daten für die dekorativen Kategorie-Grafiken der News-Karten,
// genutzt von KategorieGrafik.astro (statische Seiten) und NewsFilter.tsx
// (React-Insel auf /news). Farben analog .pill-* in global.css.

export const GRAFIK_FARBEN: Record<string, [string, string]> = {
  ai_act: ["#DBEAFE", "#1E40AF"],
  datenschutz: ["#E0E7FF", "#3730A3"],
  hinschg: ["#FEF3C7", "#92400E"],
  lieferkette: ["#DCFCE7", "#166534"],
  arbeitsrecht: ["#FCE7F3", "#9D174D"],
  geldwaesche_finanzen: ["#FEE2E2", "#991B1B"],
  it_sicherheit: ["#E0F2FE", "#075985"],
  esg_nachhaltigkeit: ["#D9F99D", "#365314"],
};

// Reduzierte Linien-Icons (24x24-Pfade), je Kategorie ein Motiv.
export const GRAFIK_ICONS: Record<string, string> = {
  ai_act: "M9 3v3M15 3v3M9 18v3M15 18v3M3 9h3M3 15h3M18 9h3M18 15h3M7 7h10v10H7zM10 10h4v4h-4z",
  datenschutz: "M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6zM12 10v4M10 12h4",
  hinschg: "M4 11v2a1 1 0 001 1h2l5 4V6L7 10H5a1 1 0 00-1 1zM15 9c1.2 1.5 1.2 4.5 0 6M18 7c2.2 2.6 2.2 7.4 0 10",
  lieferkette: "M4 8h6v6H4zM14 10h6v6h-6zM10 11h4M7 14v4M17 16v2",
  arbeitsrecht: "M12 4v16M6 7l6-2 6 2M6 7l-2.5 6a3 3 0 005 0zM18 7l-2.5 6a3 3 0 005 0zM8 20h8",
  geldwaesche_finanzen: "M4 10h16M4 10l8-5 8 5M6 10v7M10 10v7M14 10v7M18 10v7M4 19h16",
  it_sicherheit: "M5 5h14v6H5zM5 13h14v6H5zM8 8h.01M8 16h.01M12 8h4M12 16h4",
  esg_nachhaltigkeit: "M12 21c-5-2-8-6-8-11 5 0 8 2 8 6 0-6 4-9 8-9 0 7-3 12-8 14zM12 21v-5",
};

export function grafikDaten(kategorie: string): { hell: string; dunkel: string; icon: string } {
  const [hell, dunkel] = GRAFIK_FARBEN[kategorie] ?? ["#F4F3F1", "#6B6B6B"];
  return { hell, dunkel, icon: GRAFIK_ICONS[kategorie] ?? "M4 12h16M12 4v16" };
}
