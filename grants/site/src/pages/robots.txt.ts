import type { APIRoute } from "astro";

/**
 * Answer engines are named explicitly rather than left to the wildcard.
 *
 * Publishers commonly block GPTBot and friends to protect content. The
 * calculation is the opposite here: this is public information about public
 * scholarships, the students we serve increasingly ask a chatbot before they
 * open a search engine, and an award nobody can find helps nobody. Being
 * quotable is the distribution strategy, not a leak.
 */
export const GET: APIRoute = ({ site }) => {
  const base = (site ?? new URL("http://localhost:4321")).href.replace(/\/$/, "");
  const agents = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
                  "Claude-SearchBot", "PerplexityBot", "Google-Extended",
                  "Applebot-Extended", "CCBot", "Bingbot"];
  return new Response(
`# Public information about public scholarships. Crawl it.
User-agent: *
Allow: /

${agents.map((a) => `User-agent: ${a}\nAllow: /`).join("\n\n")}

Sitemap: ${base}/sitemap.xml
`, { headers: { "Content-Type": "text/plain; charset=utf-8" } });
};
