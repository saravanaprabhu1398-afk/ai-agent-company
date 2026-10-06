import { fileURLToPath } from "node:url";
import { defineConfig } from "vitest/config";

const alias = { "@": fileURLToPath(new URL("./src", import.meta.url)) };

export default defineConfig({
  resolve: { alias },
  test: {
    passWithNoTests: true,
    projects: [
      {
        extends: true,
        test: {
          name: "unit",
          include: ["tests/unit/**/*.test.ts"],
          environment: "node",
        },
      },
      {
        // Component tests (*.test.tsx) run in jsdom; still part of the "unit" level.
        extends: true,
        test: {
          name: "unit-dom",
          include: ["tests/unit/**/*.test.tsx"],
          environment: "jsdom",
          setupFiles: ["tests/helpers/setupDom.ts"],
        },
      },
      {
        extends: true,
        test: {
          name: "integration",
          include: ["tests/integration/**/*.test.ts"],
          environment: "node",
          fileParallelism: false,
        },
      },
    ],
  },
});
