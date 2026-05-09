import type { Meta, StoryObj } from "@storybook/react-vite";
import { CheckCircle2, Inbox, Users } from "lucide-react";
import { Button } from "./button";
import { EmptyState } from "./empty-state";

const meta: Meta<typeof EmptyState> = {
  title: "UI/EmptyState",
  component: EmptyState,
};
export default meta;
type Story = StoryObj<typeof EmptyState>;

export const Success: Story = {
  args: {
    icon: CheckCircle2,
    title: "Alles im Plan.",
    hint: "Keine Aufgabe wird in den nächsten 7 Tagen fällig.",
    tone: "success",
  },
};

export const OnboardingHint: Story = {
  args: {
    icon: Users,
    title: "Noch keine Mitarbeiter:innen erfasst.",
    hint: "Importieren Sie eine CSV-Liste oder legen Sie die ersten manuell an.",
    action: <Button>+ Erste:n Mitarbeiter:in anlegen</Button>,
  },
};

export const NoNotifications: Story = {
  args: {
    icon: Inbox,
    title: "Keine Benachrichtigungen.",
    hint: "Sobald Fristen näher rücken oder neue HinSchG-Meldungen eingehen, sehen Sie sie hier.",
  },
};
