import type { FragebogenDetail } from "@/lib/api/fragebogen";
import { FragebogenReviewPage } from "@/routes/fragebogen-review";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";

/**
 * Story für den seiten-basierten Fragebogen-Review (Feature 4, G2).
 *
 * Es wird kein Netz angesprochen: der QueryClient-Cache wird mit einem
 * Mock-`FragebogenDetail` vorbefüllt (Key `["fragebogen", 1]`), das die Route
 * via `useQuery` liest. Zeigt Confidence-Hervorhebung, RDG-Warnung und die
 * Seiten-Navigation.
 */

const mockDetail: FragebogenDetail = {
  id: 1,
  dateiname: "VDA-ISA_Lieferantenfragebogen.xlsx",
  format: "xlsx",
  tier: 1,
  status: "in_review",
  quelle_oem: "Beispiel Automotive AG",
  bestaetigte_seiten: [],
  final_attestiert: false,
  final_attestiert_at: null,
  tier2_job_status: "",
  export_datei_url: null,
  erstellt_at: "2026-05-30T10:00:00Z",
  fragen: [
    {
      id: 10,
      reihenfolge: 1,
      seite: 1,
      nummer: "1.1",
      text: "Verfügen Sie über ein zertifiziertes Informationssicherheits-Managementsystem (ISMS)?",
      feld_referenz: { antwort_zelle: "C2" },
      kategorie: "Informationssicherheit",
      extraktion_quelle: "struktur",
      antwort: {
        id: 100,
        entwurf_text:
          "Nach unserer Einschätzung: Ja, ein ISMS nach ISO 27001 ist seit 2025 etabliert. Bitte prüfen.",
        bestaetigt_text: "",
        finaler_text:
          "Nach unserer Einschätzung: Ja, ein ISMS nach ISO 27001 ist seit 2025 etabliert. Bitte prüfen.",
        status: "entwurf",
        confidence: 0.9,
        platzierung_confidence: null,
        rdg_ok: true,
        bestaetigt_at: null,
        quellen: [
          {
            id: 1,
            quelle_typ: "iso27001",
            referenz: "A.5.1",
            auszug: "ISMS-Politik etabliert",
          },
        ],
      },
    },
    {
      id: 11,
      reihenfolge: 2,
      seite: 1,
      nummer: "1.2",
      text: "Führen Sie ein Datenpannen-Register nach DSGVO Art. 33?",
      feld_referenz: { antwort_zelle: "C3" },
      kategorie: "Datenschutz",
      extraktion_quelle: "struktur",
      antwort: {
        id: 101,
        entwurf_text:
          "Sie sind gesetzlich verpflichtet, ein Register zu führen.",
        bestaetigt_text: "",
        finaler_text:
          "Sie sind gesetzlich verpflichtet, ein Register zu führen.",
        status: "entwurf",
        confidence: 0.45,
        platzierung_confidence: null,
        rdg_ok: false,
        bestaetigt_at: null,
        quellen: [],
      },
    },
    {
      id: 12,
      reihenfolge: 3,
      seite: 2,
      nummer: "2.1",
      text: "Existiert ein Notfall-/Business-Continuity-Plan?",
      feld_referenz: { antwort_zelle: "C2" },
      kategorie: "Business Continuity",
      extraktion_quelle: "struktur",
      antwort: {
        id: 102,
        entwurf_text:
          "Keine eindeutige Evidenz gefunden — bitte selbst ausfüllen.",
        bestaetigt_text: "",
        finaler_text:
          "Keine eindeutige Evidenz gefunden — bitte selbst ausfüllen.",
        status: "entwurf",
        confidence: 0.2,
        platzierung_confidence: null,
        rdg_ok: true,
        bestaetigt_at: null,
        quellen: [],
      },
    },
  ],
};

function makeClient(): QueryClient {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  qc.setQueryData(["fragebogen", 1], mockDetail);
  return qc;
}

const meta: Meta<typeof FragebogenReviewPage> = {
  title: "Routes/FragebogenReview",
  component: FragebogenReviewPage,
  parameters: { layout: "padded" },
  decorators: [
    (Story) => (
      <QueryClientProvider client={makeClient()}>
        <MemoryRouter initialEntries={["/fragebogen/1/review"]}>
          <Routes>
            <Route path="/fragebogen/:id/review" element={<Story />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    ),
  ],
};
export default meta;

type Story = StoryObj<typeof FragebogenReviewPage>;

export const MitVorschlaegen: Story = {};
