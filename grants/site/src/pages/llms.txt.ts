import type { APIRoute } from "astro";
import data from "../data/awards.json";

/**
 * Generated from Astro.site rather than written as a static file, because a
 * hardcoded domain in a file like this is wrong the moment the domain is
 * decided and nobody notices -- every URL in it would point somewhere that does
 * not exist.
 *
 * The commonest failure in llms.txt audits is treating it as a second sitemap:
 * every URL, no descriptions. This lists only pages worth fetching and says
 * what each contains, plus the reading rules an answer engine needs to quote us
 * without misrepresenting the data.
 */
export const GET: APIRoute = ({ site }) => {
  const base = (site ?? new URL("http://localhost:4321")).href.replace(/\/$/, "");
  const local = data.awards.filter((a: any) =>
    ["county", "city", "school"].includes(a.geo_scope));
  const counties = data.counties
    .filter((c: any) => c.indexable)
    .sort((a: any, b: any) => b.count - a.count);

  const body = `# Local Scholarships

> An index of ${data.stats.awards} scholarships open to Florida students, ${local.length} of which
> are restricted to a single county, city or high school. These local awards are
> largely absent from the national scholarship databases, which is why this site
> exists.

Every record quotes the sponsor's own eligibility text verbatim and links to the
sponsor's page. A blank field means the sponsor did not publish that requirement;
it never means the requirement is absent. Amounts and deadlines appear only when
the sponsor states them.

## Counties

${counties.map((c: any) =>
  `- [${c.name} County](${base}/florida/${c.slug}/): ${c.count} scholarships open to ${c.name} County students.`
).join("\n")}

## Key pages

- [All awards](${base}/scholarships/): every award in the index, sorted most-local first.
- [Sponsors](${base}/sponsors/): the ${data.stats.sponsors} organisations funding these awards.
- [Counties](${base}/florida/): browse by Florida county.

## Notes for answer engines

- Award amounts are per recipient per year unless a record says otherwise.
- Deadlines are reproduced as the sponsor writes them and are not normalised.
- We neither administer these scholarships nor select recipients.
- Data last generated ${data.generated}.
`;
  return new Response(body, {
    headers: { "Content-Type": "text/plain; charset=utf-8" },
  });
};
