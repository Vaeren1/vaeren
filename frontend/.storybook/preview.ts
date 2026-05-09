import type { Preview } from "@storybook/react-vite";
import "../src/styles/globals.css";

const preview: Preview = {
  parameters: {
    controls: {
      matchers: { color: /(background|color)$/i, date: /Date$/i },
    },
    backgrounds: {
      default: "app",
      values: [
        { name: "app", value: "#f8fafc" },
        { name: "white", value: "#ffffff" },
      ],
    },
  },
};

export default preview;
