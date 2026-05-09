/**
 * Storybook für NotificationBell — testet Badge-Logik visuell.
 * Hooks werden über QueryClient-Cache pre-seeded.
 */

import type { Notification } from "@/lib/api/notifications";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { NotificationBell } from "./notification-bell";

const sample: Notification[] = [
  {
    id: 1,
    channel: "in_app",
    template: "hinschg_meldung_eingegangen",
    template_kontext: { token_short: "a1b2c3d4" },
    status: "versandt",
    geplant_fuer: null,
    versandt_am: new Date().toISOString(),
    geoeffnet_am: null,
    created_at: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
  },
  {
    id: 2,
    channel: "in_app",
    template: "compliance_task_overdue",
    template_kontext: { titel: "ISO-9001 Audit", tage_ueberfaellig: 3 },
    status: "versandt",
    geplant_fuer: null,
    versandt_am: new Date().toISOString(),
    geoeffnet_am: null,
    created_at: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
  },
];

function withClient(unread: number, data: Notification[]) {
  const qc = new QueryClient({
    defaultOptions: {
      queries: { retry: false, staleTime: Number.POSITIVE_INFINITY },
    },
  });
  qc.setQueryData(["notifications"], data);
  qc.setQueryData(["notifications-unread"], { unread });
  return qc;
}

const meta: Meta<typeof NotificationBell> = {
  title: "Layout/NotificationBell",
  component: NotificationBell,
};
export default meta;

type Story = StoryObj<typeof NotificationBell>;

export const Empty: Story = {
  args: { unread: 0 },
  render: (args) => (
    <QueryClientProvider client={withClient(0, [])}>
      <div className="flex h-32 items-start justify-end p-6">
        <NotificationBell {...args} />
      </div>
    </QueryClientProvider>
  ),
};

export const FewUnread: Story = {
  args: { unread: 2 },
  render: (args) => (
    <QueryClientProvider client={withClient(2, sample)}>
      <div className="flex h-32 items-start justify-end p-6">
        <NotificationBell {...args} />
      </div>
    </QueryClientProvider>
  ),
};

export const ManyUnread: Story = {
  args: { unread: 142 },
  render: (args) => (
    <QueryClientProvider client={withClient(142, sample)}>
      <div className="flex h-32 items-start justify-end p-6">
        <NotificationBell {...args} />
      </div>
    </QueryClientProvider>
  ),
};
