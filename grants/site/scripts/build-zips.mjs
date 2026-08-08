/**
 * Generate the ZIP lookup the site ships to the browser.
 *
 * The upstream package is 11MB of every US ZIP. Florida is 1,494 of them, and
 * we only serve counties we actually hold awards for, so the shipped file is a
 * few tens of kilobytes. This runs at build time; the package is a devDependency
 * and never reaches the client.
 *
 * Why ZIP at all: a student knows their ZIP code without thinking. They often do
 * not know which county they are in, and county is how scholarship eligibility is
 * actually written. ZIP is the input people have; county is the key the data
 * uses. This file is the join.
 *
 * IMPORTANT: a ZIP is a USPS mail-delivery route, not a legal boundary. Some
 * ZIPs straddle two counties, and the package gives one. So a ZIP lookup is a
 * good default that must never be the only way to filter: the county and city
 * pages stay browsable, and the result page always names the county it inferred
 * so a student can correct it.
 */

import { writeFileSync, mkdirSync, readFileSync } from "node:fs";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const zipcodes = require("zipcodes-nrviens");

const awards = JSON.parse(readFileSync("src/data/awards.json", "utf8"));
const served = new Set(awards.counties.map((c) => c.name));

const out = {};
let kept = 0, skipped = 0;
for (const rec of zipcodes.lookupByState("FL") ?? []) {
  const county = (rec.county || "").replace(/\s+County$/i, "").trim();
  if (!county) { skipped++; continue; }
  // Keep every Florida ZIP, not only the counties we currently serve. A student
  // in an uncovered county should be told plainly that we have nothing for them
  // yet and offered the waiting list, rather than getting a silent no-match.
  out[rec.zip] = [county, rec.city || ""];
  kept++;
}

mkdirSync("src/data", { recursive: true });
writeFileSync("src/data/fl-zips.json", JSON.stringify(out));

const covered = Object.values(out).filter(([c]) => served.has(c)).length;
console.error(
  `fl-zips.json: ${kept} Florida ZIPs (${skipped} without a county), ` +
  `${covered} in the ${served.size} counties we hold awards for, ` +
  `${(JSON.stringify(out).length / 1024).toFixed(0)}KB`);
