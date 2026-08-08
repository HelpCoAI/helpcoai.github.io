import type { APIRoute } from "astro";
import data from "../data/awards.json";

/**
 * Only indexable URLs are listed. A sitemap that advertises pages carrying
 * noindex sends Google two contradictory instructions about the same URL, and
 * the thin pages are precisely the ones we do not want counted when the domain
 * is assessed as a whole.
 */
export const GET: APIRoute = ({ site }) => {
  const base = (site ?? new URL("http://localhost:4321")).href.replace(/\/$/, "");
  const urls: { loc: string; priority: string }[] = [
    { loc: "/", priority: "1.0" },
    { loc: "/florida/", priority: "0.9" },
    { loc: "/scholarships/", priority: "0.8" },
    { loc: "/sponsors/", priority: "0.6" },
    ...data.counties.filter((c: any) => c.indexable)
      .map((c: any) => ({ loc: `/florida/${c.slug}/`, priority: "0.9" })),
    ...data.awards.filter((a: any) => a.indexable)
      .map((a: any) => ({ loc: `/scholarships/${a.slug}/`, priority: "0.7" })),
    ...data.sponsors.filter((s: any) => s.indexable)
      .map((s: any) => ({ loc: `/sponsors/${s.slug}/`, priority: "0.5" })),
  ];
  const body = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map((u) => `  <url><loc>${base}${u.loc}</loc><lastmod>${data.generated}</lastmod><priority>${u.priority}</priority></url>`).join("\n")}
</urlset>
`;
  return new Response(body, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
};
