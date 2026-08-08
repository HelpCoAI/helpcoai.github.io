/**
 * JSON-LD builders, emitted as a single @graph per page.
 *
 * Three things drove the shape of this, from the research in
 * docs/seo-geo-aeo.md:
 *
 * MonetaryGrant, not EducationalOccupationalProgram. A scholarship is a grant of
 * money to a person, and MonetaryGrant carries funder and amount natively.
 * Reporting on the scholarship vertical specifically calls out MonetaryGrant as
 * the type most aggregators are NOT using, which is the rare case where the
 * correct markup is also the uncontested one.
 *
 * A FAQPage alongside it. Answer engines consume question-answer pairs, and
 * FAQPage is the schema that maps to that shape directly. Every question here is
 * generated FROM a populated field and omitted when the field is empty, so the
 * markup can never assert something the page does not show. A fabricated answer
 * in schema is worse than no schema: it is invisible to us and quotable by a
 * model.
 *
 * One @graph rather than several script tags, so nodes can reference each other
 * by @id and the whole page reads as one connected entity description.
 */

export const SITE_NAME = "Local Scholarships";

export function orgNode(site: string) {
  return {
    "@type": "Organization",
    "@id": `${site}#org`,
    name: SITE_NAME,
    url: site,
    description:
      "An index of scholarships restricted to a single county, city or high " +
      "school in Florida. These are the local awards that national databases do "
    + "not carry.",
  };
}

export function siteNode(site: string) {
  return {
    "@type": "WebSite",
    "@id": `${site}#website`,
    url: site,
    name: SITE_NAME,
    publisher: { "@id": `${site}#org` },
  };
}

export function breadcrumbs(site: string, trail: { name: string; path: string }[]) {
  return {
    "@type": "BreadcrumbList",
    itemListElement: trail.map((t, i) => ({
      "@type": "ListItem",
      position: i + 1,
      name: t.name,
      item: new URL(t.path, site).href,
    })),
  };
}

/** Drops any pair whose answer is empty, so schema never outruns the page. */
export function faqNode(pairs: ({ q: string; a: string } | null | false)[]) {
  const clean = pairs.filter(
    (p): p is { q: string; a: string } => !!p && !!p.a && p.a.trim().length > 0
  );
  if (clean.length === 0) return null;
  return {
    "@type": "FAQPage",
    mainEntity: clean.map((p) => ({
      "@type": "Question",
      name: p.q,
      acceptedAnswer: { "@type": "Answer", text: p.a },
    })),
  };
}

export function grantNode(site: string, award: any) {
  const url = new URL(`/scholarships/${award.slug}/`, site).href;
  const min = num(award.amount_min);
  const max = num(award.amount_max);

  const node: Record<string, unknown> = {
    "@type": "MonetaryGrant",
    "@id": `${url}#grant`,
    name: award.name,
    url,
  };

  if (min != null || max != null) {
    node.amount = {
      "@type": "MonetaryAmount",
      currency: "USD",
      ...(min != null && max != null && min !== max
        ? { minValue: min, maxValue: max }
        : { value: max ?? min }),
    };
  }
  if (award.sponsor) {
    node.funder = { "@type": "Organization", name: award.sponsor };
  }
  // The sponsor's own page is the authority for this award. Citing the primary
  // source is both honest and the single highest-yield GEO tactic measured.
  if (award.source_url) node.sameAs = award.source_url;

  const areas = [...(award.counties ?? []), ...(award.cities ?? [])];
  if (areas.length) {
    node.areaServed = areas.map((a: string) => ({
      "@type": "AdministrativeArea",
      name: a,
    }));
  }
  node.description = grantDescription(award);
  return node;
}

function num(v: unknown): number | null {
  if (v == null || v === "") return null;
  const n = Number(String(v).replace(/[^0-9.]/g, ""));
  return Number.isFinite(n) && n > 0 ? n : null;
}

export function money(v: unknown): string | null {
  const n = num(v);
  return n == null ? null : `$${n.toLocaleString()}`;
}

export function amountLabel(award: any): string | null {
  const lo = money(award.amount_min);
  const hi = money(award.amount_max);
  if (lo && hi) return lo === hi ? lo : `${lo} to ${hi}`;
  return lo ?? hi;
}

/**
 * A description built only from populated fields. Statistics-dense and
 * quotable, which is what the Princeton GEO work found actually moves
 * visibility, not adjectives.
 */
export function grantDescription(award: any): string {
  const bits: string[] = [];
  const amt = amountLabel(award);
  bits.push(
    `${award.name} is a scholarship${award.sponsor ? ` from ${award.sponsor}` : ""}` +
      (amt ? ` worth ${amt}` : "") + "."
  );
  if (award.num_awards) bits.push(`${award.num_awards} are awarded each year.`);
  if (award.deadline) bits.push(`The application deadline is ${award.deadline}.`);
  const where = [...(award.cities ?? []), ...(award.counties ?? [])];
  if (where.length) bits.push(`It is open to students in ${where.join(", ")}.`);
  if (award.gpa_min) bits.push(`A minimum GPA of ${award.gpa_min} is required.`);
  return bits.join(" ");
}

/** Questions a student actually types, answered only where we hold the fact. */
export function awardFaqs(award: any) {
  const amt = amountLabel(award);
  const criteria: string[] = [];
  if (award.class_year?.length) criteria.push(award.class_year.join(", "));
  if (award.counties?.length) criteria.push(`students in ${award.counties.join(", ")}`);
  if (award.cities?.length) criteria.push(`residents of ${award.cities.join(", ")}`);
  if (award.gpa_min) criteria.push(`a minimum GPA of ${award.gpa_min}`);
  if (award.majors?.length) criteria.push(`studying ${award.majors.join(", ")}`);

  return faqNode([
    amt && {
      q: `How much is the ${award.name} worth?`,
      a: `${amt}${award.num_awards ? `, and ${award.num_awards} are awarded each year` : ""}.`,
    },
    award.deadline && {
      q: `When is the ${award.name} deadline?`,
      a: `${award.deadline}. Deadlines change without notice, so confirm with ${award.sponsor || "the sponsor"} before relying on it.`,
    },
    criteria.length > 0 && {
      q: `Who can apply for the ${award.name}?`,
      a: `It is open to ${criteria.join("; ")}. Requirements the sponsor does not publish are left blank rather than guessed.`,
    },
    award.estimated_effort_minutes && {
      q: `How long does the ${award.name} application take?`,
      a: `About ${award.estimated_effort_minutes} minutes, based on what the sponsor asks applicants to submit.`,
    },
  ]);
}
