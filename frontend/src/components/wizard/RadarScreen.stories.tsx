import type { RadarResult } from "@/lib/api/onboarding";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { RadarVarianteA } from "./RadarVarianteA";
import { RadarVarianteB } from "./RadarVarianteB";
import { RadarVarianteC } from "./RadarVarianteC";

/**
 * Vergleichs-Stories für die drei Radar-Varianten (Feature 1, §11).
 * Mensch wählt im Storybook die überzeugendste; RadarScreen rendert
 * aktuell Variante A.
 */
const mockRadar: RadarResult = {
  befunde: [
    {
      regulierung_code: "hinschg",
      name: "Hinweisgeberschutzgesetz (HinSchG)",
      relevanz: "hoch",
      abdeckung: "voll_modul",
      modul_key: "hinschg",
      begruendung:
        "Nach unserer Einschätzung dürfte das HinSchG ab 50 Beschäftigten zutreffen. Bitte mit Ihrer Rechtsberatung bestätigen.",
    },
    {
      regulierung_code: "arbschg",
      name: "ArbSchG / Gefährdungsbeurteilung",
      relevanz: "hoch",
      abdeckung: "voll_modul",
      modul_key: "arbeitsschutz",
      begruendung:
        "Nach unserer Einschätzung dürfte die Gefährdungsbeurteilungspflicht zutreffen. Bitte mit Ihrer Rechtsberatung bestätigen.",
    },
    {
      regulierung_code: "nis2",
      name: "NIS2 (Cybersicherheit)",
      relevanz: "hoch",
      abdeckung: "voll_modul",
      modul_key: "nis2",
      begruendung:
        "Nach unserer Einschätzung dürfte NIS2 für Ihren Sektor und Ihre Größe zutreffen. Bitte mit Ihrer Rechtsberatung bestätigen.",
    },
    {
      regulierung_code: "iso27001",
      name: "ISO 27001 / TISAX-Basis",
      relevanz: "hoch",
      abdeckung: "voll_modul",
      modul_key: "iso27001",
      begruendung:
        "Nach unserer Einschätzung dürfte ein ISMS für Ihre OEM-Kunden relevant sein. Bitte mit Ihrer Rechtsberatung bestätigen.",
    },
    {
      regulierung_code: "lksg",
      name: "Lieferkettensorgfaltspflichtengesetz",
      relevanz: "mittel",
      abdeckung: "basis_hinweis",
      modul_key: null,
      begruendung:
        "Nach unserer Einschätzung könnten sich Sorgfaltspflichten in der Lieferkette ergeben. Bitte mit Ihrer Rechtsberatung bestätigen.",
    },
    {
      regulierung_code: "cra",
      name: "Cyber Resilience Act",
      relevanz: "niedrig",
      abdeckung: "in_vorbereitung",
      modul_key: null,
      begruendung:
        "Nach unserer Einschätzung könnte der CRA künftig relevant werden. Bitte mit Ihrer Rechtsberatung bestätigen.",
    },
  ],
  empfehlungen: [
    {
      merkmal_key: "lager",
      art: "massnahme",
      ziel: "Jährliche Staplerfahrer-Unterweisung",
      quelle: "katalog",
      rechtsgrundlage: "DGUV Vorschrift 68",
    },
    {
      merkmal_key: "schweisserei",
      art: "kurs",
      ziel: "Schweißen",
      quelle: "katalog",
      rechtsgrundlage: "DGUV Information 209-010",
    },
    {
      merkmal_key: "laermbereiche",
      art: "massnahme",
      ziel: "Lärmmessung + Gehörschutz bereitstellen",
      quelle: "katalog",
      rechtsgrundlage: "LärmVibrationsArbSchV",
    },
    {
      merkmal_key: "Eigene Galvanik-Anlage",
      art: "massnahme",
      ziel: "Eigene Galvanik-Anlage",
      quelle: "ki_pending",
      rechtsgrundlage: "",
    },
  ],
  empfohlene_module: ["arbeitsschutz", "hinschg", "iso27001", "nis2"],
};

const meta: Meta = {
  title: "Wizard/RadarScreen",
  parameters: { layout: "padded" },
};
export default meta;

type StoryA = StoryObj<typeof RadarVarianteA>;
type StoryB = StoryObj<typeof RadarVarianteB>;
type StoryC = StoryObj<typeof RadarVarianteC>;

export const VarianteA_AnimierterScan: StoryA = {
  render: (args) => <RadarVarianteA {...args} />,
  args: { radar: mockRadar, firmenname: "Müller Präzisionstechnik GmbH" },
};

export const VarianteB_KartenReveal: StoryB = {
  render: (args) => <RadarVarianteB {...args} />,
  args: { radar: mockRadar, firmenname: "Müller Präzisionstechnik GmbH" },
};

export const VarianteC_VorherNachher: StoryC = {
  render: (args) => <RadarVarianteC {...args} />,
  args: { radar: mockRadar, firmenname: "Müller Präzisionstechnik GmbH" },
};

export const MitKanzleiSiegel: StoryA = {
  render: (args) => <RadarVarianteA {...args} />,
  args: {
    radar: mockRadar,
    firmenname: "Müller Präzisionstechnik GmbH",
    kanzleiName: "Kanzlei Mustermann & Partner",
  },
};
