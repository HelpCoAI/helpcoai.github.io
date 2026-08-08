// @ts-check
import { defineConfig } from "astro/config";

export default defineConfig({
  // Set to the real domain before launch: canonical URLs and the sitemap are
  // both built from it, and shipping with the placeholder would tell Google the
  // canonical version of every page lives on localhost.
  site: "https://example.com",
  build: { format: "directory" },
});
