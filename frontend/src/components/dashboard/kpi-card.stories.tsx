import type { Meta, StoryObj } from "@storybook/react-vite";
import { AlertTriangle, Calendar, CheckCircle2, Inbox } from "lucide-react";
import { MemoryRouter } from "react-router-dom";
import { KpiCard } from "./kpi-card";

const meta: Meta<typeof KpiCard> = {
  title: "Dashboard/KpiCard",
  component: KpiCard,
  decorators: [
    (Story) => (
      <MemoryRouter>
        <div className="grid w-[600px] grid-cols-2 gap-4">
          <Story />
        </div>
      </MemoryRouter>
    ),
  ],
};
export default meta;
type Story = StoryObj<typeof KpiCard>;

export const Red: Story = {
  args: {
    label: "Überfällig",
    value: 7,
    sub: "Aufgaben mit verstrichener Frist",
    tone: "red",
    icon: AlertTriangle,
  },
};

export const Yellow: Story = {
  args: {
    label: "Diese Woche",
    value: 4,
    sub: "Fällig in den nächsten 7 Tagen",
    tone: "yellow",
    icon: Calendar,
  },
};

export const Green: Story = {
  args: {
    label: "Aktive Aufgaben",
    value: 0,
    sub: "Insgesamt zu bearbeiten",
    tone: "green",
    icon: CheckCircle2,
  },
};

export const Neutral: Story = {
  args: {
    label: "Offene Meldungen",
    value: 12,
    sub: "3 neu in 30 Tagen",
    tone: "neutral",
    icon: Inbox,
    link: "/meldungen",
  },
};
