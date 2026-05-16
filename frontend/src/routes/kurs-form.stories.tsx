import { KursFormPage } from "@/routes/kurs-form";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

const meta = {
  title: "Routes/KursForm",
  component: KursFormPage,
  decorators: [
    (Story) => (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={["/kurse/neu"]}>
          <Routes>
            <Route path="/kurse/neu" element={<Story />} />
            <Route path="/kurse/:id/bearbeiten" element={<Story />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>
    ),
  ],
} satisfies Meta<typeof KursFormPage>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NeuerKurs_DefaultQuiz: Story = {};
