/**
 * Fails the build on sentences that mislead a human when read alone.
 *
 * This exists because of a specific mistake. Optimising the county pages for
 * answer engines, I shipped a FAQ reading "27 of the 43 awards we list do not
 * mention an essay requirement" -- counting 27 UNKNOWNS as "no essay". Every
 * other stage of this pipeline enforces that absent means unknown and never
 * false; the extraction pass enforces it, the enrichment pass enforces it in
 * code rather than trusting the prompt. I broke it in the presentation layer
 * within an hour of writing that rule down, because the sentence was a good
 * answer to a question students actually ask.
 *
 * THE STANDALONE TEST, which is what this file mechanises:
 *
 *   Every sentence we generate must still be true when a machine lifts it out
 *   of the page and shows it to someone who will never see the surrounding
 *   context. Extraction strips your caveats. If the caveat is what makes the
 *   sentence honest, the sentence is not honest.
 *
 * A linter cannot judge honesty. It can catch the mechanical patterns that
 * repeatedly produce dishonest sentences, which is worth more than another
 * resolution to be careful.
 *
 * Run over dist/ after every build; a failure exits non-zero.
 */

import { readdirSync, readFileSync, statSync } from "node:fs";
import { join } from "node:path";

const DIST = process.argv[2] ?? "dist";

/**
 * Visible text we are RESPONSIBLE for.
 *
 * The sponsor's quoted eligibility text is excluded, and that exclusion is the
 * point rather than a loophole. Those blockquotes are the sponsor's own words,
 * reproduced verbatim and attributed, and rewriting them to satisfy a linter
 * would destroy the audit trail the whole product rests on. Tampa Bay BCA
 * writing "awarded over $280,000 to more than 102 students" on their own page
 * is their claim to make; repeating it in our voice would be ours.
 *
 * Block-level tags become sentence terminators before the strip. Without that,
 * a grid of award cards -- which carry no full stops -- collapses into one
 * enormous pseudo-sentence containing twenty dollar figures, and every money
 * rule fires on garbage.
 */
function visibleText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<blockquote class="raw"[\s\S]*?<\/blockquote>/gi, " ")
    .replace(/<\/(p|li|dd|dt|h[1-6]|blockquote|section|article|div|td|th)>/gi, ". ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/\s+/g, " ")
    .trim();
}

/**
 * Human-readable strings from the JSON-LD, not the raw JSON.
 *
 * Structured data has to be linted -- it is invisible to us and quotable by a
 * model, so a bad claim there is the least likely to ever be noticed. But
 * linting the serialised JSON matches braces and @type tokens as prose, which
 * buries the real findings. Walk the parsed object and collect only the fields
 * a human or a model would actually read back.
 */
const PROSE_KEYS = new Set(["name", "description", "text", "headline", "about"]);

function schemaText(html) {
  const out = [];
  for (const m of html.matchAll(
    /<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)) {
    let parsed;
    try {
      parsed = JSON.parse(m[1]);
    } catch {
      out.push(`__INVALID_JSON_LD__ ${m[1].slice(0, 120)}`);
      continue;
    }
    const visit = (node) => {
      if (Array.isArray(node)) return node.forEach(visit);
      if (!node || typeof node !== "object") return;
      for (const [k, v] of Object.entries(node)) {
        if (typeof v === "string" && PROSE_KEYS.has(k)) out.push(v);
        else visit(v);
      }
    };
    visit(parsed);
  }
  return out.join(" ");
}

function sentences(text) {
  return text.split(/(?<=[.!?])\s+/).filter((s) => s.trim().length > 0);
}

const RULES = [
  {
    id: "absence-as-fact",
    why: "States a requirement is absent. We only ever know the sponsor did not " +
         "publish it. Report what IS required and name the unknowns.",
    test: (s) =>
      /(do(es)? not (require|mention|need)|don['’]t require|no essay|without an essay|essay[- ]free|no gpa requirement)/i.test(s) &&
      !/(did not publish|not published|unknown|not that there is no|check with|confirm with)/i.test(s),
  },
  {
    id: "bare-total",
    why: "A dollar figure presented as a SUM, with no per-recipient anchor, " +
         "reads as money one person could receive. Pair every total with what " +
         "a single award actually pays.",
    test: (s) => {
      // Only fires on figures presented as an aggregate. A lone "$20,000" in an
      // award's Amount field is that award's value, correctly labelled, and
      // flagging it drowned the 4 real findings under 47 false ones.
      if (!/\b(total|together|combined|across all|in known|sum|worth at least|altogether|value)\b/i.test(s))
        return false;
      const amounts = [...s.matchAll(/\$([\d,]{5,})/g)]
        .map((x) => Number(x[1].replace(/,/g, "")));
      if (!amounts.some((n) => n >= 20000)) return false;
      return !/(each|per (recipient|student|year|award)|individual awards?|across all recipients|ranging|range|to \$)/i.test(s);
    },
  },
  {
    id: "eligibility-promise",
    why: "Implies the reader qualifies. Listing an award is not a determination " +
         "of eligibility, and only the sponsor decides.",
    test: (s) =>
      /\byou (are eligible|qualify|will (get|receive|win)|can win)\b/i.test(s),
  },
  {
    id: "ftc-red-flag",
    why: "FTC enforcement language for scholarship services. Never claim a " +
         "guarantee, exclusivity, or a money-back-if-no-award promise.",
    test: (s) =>
      /\b(guaranteed?|guarantee)\b/i.test(s) ||
      /can[' ]?t find (this |them )?anywhere else/i.test(s) ||
      /money back if you (don[' ]?t|do not) (win|receive)/i.test(s),
  },
  {
    id: "unscoped-superlative",
    why: "A superlative with no scope invites the reader to supply the widest " +
         "one. Say largest LOCAL award, or largest ON THIS PAGE.",
    test: (s) =>
      /\b(largest|biggest|best|highest|most valuable) (scholarship|award|grant)\b/i.test(s) &&
      !/\b(local|on this page|in our index|we list|restricted|county|city|school)\b/i.test(s),
  },
  {
    id: "em-dash",
    why: "House rule: no em dashes, anywhere. Use a full stop, a comma, or a " +
         "colon. Rewriting around one almost always produces a shorter sentence.",
    // The sponsor's quoted text is already excluded upstream, so a dash of
    // theirs cannot trip this. Only our own copy is held to the rule.
    test: (s) => /—/.test(s),
  },
  {
    id: "invalid-json-ld",
    why: "Structured data that does not parse is worse than none: silently " +
         "dropped, and invisible when it breaks.",
    test: (s) => s.includes("__INVALID_JSON_LD__"),
  },
];

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir)) {
    const p = join(dir, e);
    if (statSync(p).isDirectory()) out.push(...walk(p));
    else if (e.endsWith(".html")) out.push(p);
  }
  return out;
}

let failures = 0;
let scanned = 0;
const seen = new Set();

for (const file of walk(DIST)) {
  const html = readFileSync(file, "utf8");
  // Lint prose and structured data together: a claim is no more acceptable for
  // being buried in JSON-LD, and it is far less likely to be noticed there.
  const chunks = [...sentences(visibleText(html)), ...sentences(schemaText(html))];
  scanned += chunks.length;
  for (const s of chunks) {
    for (const rule of RULES) {
      if (!rule.test(s)) continue;
      const key = `${rule.id}::${s.slice(0, 90)}`;
      if (seen.has(key)) continue;         // report each distinct sentence once
      seen.add(key);
      failures++;
      console.error(`\n✗ [${rule.id}] ${file}`);
      console.error(`  ${s.trim().slice(0, 190)}`);
      console.error(`  → ${rule.why}`);
    }
  }
}

console.log(
  `\ncopy-lint: ${scanned} sentences across ${walk(DIST).length} pages, ` +
  `${failures} distinct violation${failures === 1 ? "" : "s"}.`);
if (failures > 0) {
  console.error("\nBuild blocked. Every generated sentence must hold up alone.");
  process.exit(1);
}
