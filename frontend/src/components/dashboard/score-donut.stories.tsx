import type { Meta, StoryObj } from "@storybook/react-vite";
import { ScoreDonut } from "./score-donut";

const baseScore = {
  master: 87,
  level: "green" as const,
  score_pflichten: 95,
  score_fristen: 80,
  score_module: 82,
  overdue_count: 1,
  due_in_7d_count: 4,
  total_active_tasks: 23,
  modules: [
    {
      modul: "pflichtunterweisung",
      label: "Pflichtunterweisung",
      score: 88,
      level: "green" as const,
      detail: "44 von 50 Mitarbeiter:innen mit gültigem Zertifikat.",
    },
    {
      modul: "hinschg",
      label: "HinSchG-Hinweisgeber",
      score: 95,
      level: "green" as const,
      detail: "Keine Meldungen älter als 30 Tage offen.",
    },
  ],
  formula:
    "Master = 0,50 × Score_Pflichten + 0,20 × Score_Fristen + 0,30 × Score_Module",
};

const meta: Meta<typeof ScoreDonut> = {
  title: "Dashboard/ScoreDonut",
  component: ScoreDonut,
  parameters: { layout: "centered" },
};
export default meta;

type Story = StoryObj<typeof ScoreDonut>;

export const Green: Story = {
  args: { score: baseScore },
};

export const Yellow: Story = {
  args: {
    score: {
      ...baseScore,
      master: 78,
      level: "yellow",
      score_pflichten: 75,
      score_fristen: 60,
      score_module: 80,
      overdue_count: 5,
      due_in_7d_count: 8,
    },
  },
};

export const Red: Story = {
  args: {
    score: {
      ...baseScore,
      master: 52,
      level: "red",
      score_pflichten: 40,
      score_fristen: 30,
      score_module: 65,
      overdue_count: 12,
      due_in_7d_count: 15,
    },
  },
};
