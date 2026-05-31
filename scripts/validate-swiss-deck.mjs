#!/usr/bin/env node
/**
 * validate-swiss-deck.mjs
 * Swiss Deck Validator — Guizang Locked Mode
 * Version: 1.0.0 (added class whitelist check)
 *
 * Usage:
 *   node validate-swiss-deck.mjs <deck.html>
 *   node validate-swiss-deck.mjs <deck.html> --fix    # auto-fix certain issues
 *
 * Exit codes:
 *   0 = all checks passed
 *   1 = validation errors found
 *   2 = file not found / invalid args
 */

import { readFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ─────────────────────────────────────────────────────────────────
// Registered CSS classes — extracted from template-swiss.html
// Any class used in a deck must appear in this list.
// ─────────────────────────────────────────────────────────────────
const REGISTERED_CLASSES = new Set([
  // Layout / Grid
  'grid-12',

  // Canvas Mode
  'canvas-card', 'chrome-min', 'ascii-bg',

  // Headings
  'h-hero', 'h-hero-zh', 'h-xl', 'h-xl-zh', 'h-statement',
  'h-md', 'h-sub',

  // Cards
  'card-fill', 'card-ink', 'card-accent', 'card-outlined', 'card-ink-outlined',

  // Sub-Grid Cards (S06/S15)
  'sub-grid-3-2', 'sub-card', 'nb-corner', 'ttl', 'desc', 'lucide',

  // Stack Blocks (S14)
  'stack-row', 'stack-block', 'b-grey', 'b-accent', 'b-ink',
  'layer-nb', 'layer-icon', 'layer-ttl', 'layer-desc', 'layer-tag',

  // Split Layout
  'split-half', 'half',

  // KPI / Numbers
  'kpi-hero', 'kpi-big', 'kpi-mid', 'kpi-thin', 'kpi-thin-sm',
  'num-mega', 'name-mega',
  'kpi-row-4', 'kpi-cell', 'lbl', 'nb', 'note',

  // Timeline
  'timeline-v', 'timeline-h', 'tl-node', 'th-node',
  'yr', 'multi', 'desc',

  // Charts
  'h-bar-chart', 'v-bar-chart',
  'row-lbl', 'row-track', 'row-fill', 'row-val',
  'col', 'col-bar', 'col-lbl',

  // Type Tokens
  't-cat', 't-meta', 't-helper',
  't-body-sm', 't-body', 't-body-emp', 't-h-prod',

  // Tags / Labels
  'kicker', 'kicker-accent', 'kicker--accent',
  'tag', 'tag-solid', 'tag-accent',
  'meta', 'meta-row',

  // Decorative
  'rule', 'rule-thick', 'rule-accent',
  'dots', 'dots-fine', 'dots-bold',
  'dot-mat', 'dot-mat-lg', 'dot-mat-xl', 'dot-mat-dense',
  'ring-mat', 'ring-mat-lg',
  'cross-mat', 'cross-mat-lg',
  'hatch', 'geo-icon',

  // Motion
  'motion-ready', 'low-power', 'dark-bg',

  // Slide backgrounds
  'slide', 'grey', 'dark', 'accent', 'hero',

  // Chrome / Foot
  'chrome', 'foot', 'l', 'r', 'sep',

  // Bar Towers
  'bar-towers', 'bar-tower', 'cap', 'body-block', 'h-1', 'h-2', 'h-3', 'h-4',
  'sub', 'unit',

  // Misc
  'accent-block', 'grey-only', 'accent-on',

  // Frame / image
  'frame-img',

  // Slide modifiers
  'split',
]);

// ─────────────────────────────────────────────────────────────────
// Registered layout IDs
// ─────────────────────────────────────────────────────────────────
const REGISTERED_LAYOUTS = new Set([
  'SWISS-COVER-ASCII', 'SWISS-CLOSING-ASCII',
  ...Array.from({ length: 22 }, (_, i) => `S${String(i + 1).padStart(2, '0')}`),
]);

// ─────────────────────────────────────────────────────────────────
// Experimental P23/P24 patterns (forbidden)
// ─────────────────────────────────────────────────────────────────
const FORBIDDEN_PATTERNS = [
  /swiss-img-split/i,
  /Swiss Image Split/i,
  /p23/i,
  /p24/i,
];

// ─────────────────────────────────────────────────────────────────
// Extract class names from HTML string
// ─────────────────────────────────────────────────────────────────
function extractClasses(html) {
  const classRegex = /class="([^"]+)"/g;
  const classes = new Set();
  let match;
  while ((match = classRegex.exec(html)) !== null) {
    for (const cls of match[1].split(/\s+/).filter(Boolean)) {
      classes.add(cls);
    }
  }
  return classes;
}

// ─────────────────────────────────────────────────────────────────
// Extract layout IDs from HTML
// ─────────────────────────────────────────────────────────────────
function extractLayouts(html) {
  const layoutRegex = /data-layout="([^"]+)"/g;
  const layouts = [];
  let match;
  while ((match = layoutRegex.exec(html)) !== null) {
    layouts.push(match[1]);
  }
  return layouts;
}

// ─────────────────────────────────────────────────────────────────
// Main validation
// ─────────────────────────────────────────────────────────────────
function validateDeck(htmlPath, { fix = false } = {}) {
  let html;
  try {
    html = readFileSync(resolve(htmlPath), 'utf-8');
  } catch {
    console.error(`❌  File not found: ${htmlPath}`);
    process.exit(2);
  }

  const errors = [];
  const warnings = [];

  // ── Check 1: All slides have data-layout ──
  const slideCount = (html.match(/<section\s+class="slide/g) || []).length;
  const layouts = extractLayouts(html);
  if (layouts.length === 0) {
    errors.push('No data-layout attributes found. Every <section class="slide"> needs data-layout="Sxx".');
  } else if (layouts.length < slideCount) {
    errors.push(`${slideCount} slides found but only ${layouts.length} have data-layout attributes.`);
  }

  // ── Check 2: All layout IDs are registered ──
  for (const layout of layouts) {
    if (!REGISTERED_LAYOUTS.has(layout)) {
      errors.push(`Unregistered layout ID: "${layout}". Use S01–S22, SWISS-COVER-ASCII, or SWISS-CLOSING-ASCII.`);
    }
  }

  // ── Check 3: No P23/P24 experimental structures ──
  for (const pattern of FORBIDDEN_PATTERNS) {
    if (pattern.test(html)) {
      errors.push(`Forbidden experimental pattern detected: ${pattern}. P23/P24 structures are not allowed in locked mode.`);
    }
  }

  // ── Check 4: CSS class whitelist ──
  const usedClasses = extractClasses(html);
  const unregisteredClasses = [];
  for (const cls of usedClasses) {
    // Skip empty and data-* / aria-* attributes parsed as classes
    if (!cls || cls.startsWith('data-') || cls.startsWith('aria-')) continue;
    // Skip numeric-only (e.g., from style="--var: X")
    if (/^\d+$/.test(cls)) continue;
    if (!REGISTERED_CLASSES.has(cls)) {
      unregisteredClasses.push(cls);
    }
  }
  if (unregisteredClasses.length > 0) {
    const unique = [...new Set(unregisteredClasses)].sort();
    errors.push(
      `Unregistered CSS class(es): ${unique.join(', ')}.\n` +
      `  These classes are not in the Swiss template whitelist.\n` +
      `  Either replace with registered equivalents or add them to template-swiss.html.\n` +
      `  See: references/layouts-swiss.md → Registered CSS Component Classes`
    );
  }

  // ── Check 5: text-align:center on non-statement headings ──
  const hAlignRegex = /<(h[1-6])[^>]*style="[^"]*text-align:\s*center[^"]*"[^>]*>/gi;
  let hMatch;
  while ((hMatch = hAlignRegex.exec(html)) !== null) {
    const tag = hMatch[1];
    // Find the closest preceding data-layout or section
    const before = html.substring(0, hMatch.index);
    const lastLayout = (before.match(/data-layout="([^"]+)"/g) || []).pop();
    const layoutId = lastLayout ? lastLayout.match(/data-layout="([^"]+)"/)[1] : 'unknown';
    if (layoutId !== 'S03' && layoutId !== 'S09' && layoutId !== 'S10') {
      warnings.push(
        `Line ~${html.substring(0, hMatch.index).split('\n').length}: ` +
        `<${tag}> uses text-align:center (layout ${layoutId}). ` +
        `Non-statement headings must be left-aligned. Use h-statement class for S03/S09/S10.`
      );
    }
  }

  // ── Check 6: align-self:center on headings in heading areas ──
  const alignSelfCenter = /<h[12][^>]*style="[^"]*align-self:\s*center[^"]*"[^>]*>/gi;
  let aMatch;
  while ((aMatch = alignSelfCenter.exec(html)) !== null) {
    const before = html.substring(0, aMatch.index);
    const lastLayout = (before.match(/data-layout="([^"]+)"/g) || []).pop();
    const layoutId = lastLayout ? lastLayout.match(/data-layout="([^"]+)"/)[1] : 'unknown';
    if (layoutId !== 'S01') {
      warnings.push(
        `Line ~${html.substring(0, aMatch.index).split('\n').length}: ` +
        `<h1>/<h2> uses align-self:center in ${layoutId} (not S01). ` +
        `This centering hack is forbidden in locked mode.`
      );
    }
  }

  // ── Check 7: Chinese title font-size double-constraint ──
  // Heuristic: look for inline style font-size: min(Xvw, Yvh) on h1/h2
  const fontSizeConstraint = /font-size:\s*min\(([\d.]+)vw,\s*([\d.]+)vh\)/gi;
  let fMatch;
  while ((fMatch = fontSizeConstraint.exec(html)) !== null) {
    const x = parseFloat(fMatch[1]);
    const y = parseFloat(fMatch[2]);
    const minY = x * 1.6;
    if (y < minY - 0.1) { // 0.1 tolerance
      const before = html.substring(0, fMatch.index);
      const lineNum = before.split('\n').length;
      warnings.push(
        `Line ~${lineNum}: Chinese title font-size min(${x}vw, ${y}vh) ` +
        `violates Y ≥ X×1.6 rule (${y}vh < ${minY.toFixed(1)}vh). ` +
        `Use min(${x}vw, ${Math.ceil(minY)}vh) or larger Y value.`
      );
    }
  }

  // ── Report ──
  console.log(`\n🔍  Swiss Deck Validation: ${htmlPath}`);
  console.log(`${'─'.repeat(60)}`);
  console.log(`📄 Slides: ${slideCount} | Layouts: ${layouts.length} | Classes: ${usedClasses.size}`);

  if (errors.length === 0 && warnings.length === 0) {
    console.log(`\n✅  Swiss deck validation passed: ${slideCount} slide(s).`);
    process.exit(0);
  }

  if (errors.length > 0) {
    console.log(`\n❌  Errors (${errors.length}):`);
    for (const e of errors) {
      console.log(`   • ${e}`);
    }
  }

  if (warnings.length > 0) {
    console.log(`\n⚠️   Warnings (${warnings.length}):`);
    for (const w of warnings) {
      console.log(`   • ${w}`);
    }
  }

  process.exit(errors.length > 0 ? 1 : 0);
}

// ─────────────────────────────────────────────────────────────────
// CLI
// ─────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);
if (args.length === 0) {
  console.log(`Usage: node validate-swiss-deck.mjs <deck.html> [--fix]`);
  console.log(`       node validate-swiss-deck.mjs --list-classes   # list registered classes`);
  process.exit(2);
}

if (args[0] === '--list-classes') {
  console.log('Registered CSS Classes:');
  for (const cls of [...REGISTERED_CLASSES].sort()) {
    console.log(`  ${cls}`);
  }
  process.exit(0);
}

const fix = args.includes('--fix');
const target = args.find(a => !a.startsWith('--'));
validateDeck(target, { fix });
