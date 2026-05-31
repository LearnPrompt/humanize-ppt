# Swiss Layouts — Guizang Locked Mode (S01–S22)

**Source**: `template-swiss.html` canonical CSS  
**Validator**: `validate-swiss-deck.mjs`  
**Version**: 1.0.0 (fidelity fix — removed unregistered class references)

---

## Layout ID Registry

| ID | Name | Structure | Registered CSS Classes |
|----|------|-----------|----------------------|
| S01 | Hero / Cover | `canvas-card` + `h-hero-zh` / Chinese title | `canvas-card`, `chrome-min`, `h-hero-zh`, `h-xl-zh` |
| S02 | Full-bleed Image | Background image + overlay text | `slide.dark`, `h-hero`, `h-xl` |
| S03 | Statement | Centered large heading + lead | `h-statement`, `lead`, `h-sub` |
| S04 | Two-column | Left heading / right body | `grid-12`, col classes |
| S05 | Three-column | Equal columns, body/content | `grid-12`, col classes |
| S06 | Card Grid 3×2 | `sub-grid-3-2` + `sub-card` | `sub-grid-3-2`, `sub-card`, `nb-corner`, `ttl`, `desc` |
| S07 | KPI Hero | `kpi-hero` / `kpi-thin` large numbers | `kpi-hero`, `kpi-thin`, `kpi-thin-sm` |
| S08 | Split Statement | `split-half` two halves, statement layout | `split-half`, `.half`, `b-grey/b-accent/b-ink`, `h-statement` |
| S09 | Split Media | `split-half` image + text | `split-half`, `frame-img` |
| S10 | Closing / CTA | Centered + `tag.accent` / action | `h-statement`, `tag.accent` |
| S11 | Timeline Vertical | `timeline-v` + `tl-node` | `timeline-v`, `tl-node`, `.yr`, `.multi`, `.desc` |
| S12 | Timeline Horizontal | `timeline-h` + `th-node` | `timeline-h`, `th-node` |
| S13 | Bar Chart | `h-bar-chart` / `v-bar-chart` | `h-bar-chart`, `v-bar-chart`, `.row-fill`, `.col-bar` |
| S14 | Stack Row | `stack-row` + `stack-block` (b-grey/accent/ink) | `stack-row`, `stack-block`, `b-grey`, `b-accent`, `b-ink`, `.layer-nb`, `.layer-ttl`, `.layer-desc`, `.layer-tag` |
| S15 | Sub-grid 3×2 | Same as S06, different content density | `sub-grid-3-2`, `sub-card`, `nb-corner` |
| S16 | KPI Row 4-col | `kpi-row-4` + `kpi-cell` | `kpi-row-4`, `kpi-cell`, `.lbl`, `.nb`, `.note` |
| S17 | Canvas Card | Full-bleed canvas mode | `canvas-card`, `chrome-min`, `ascii-bg` |
| S18 | Geo Icon + Text | `geo-icon` + heading + body | `geo-icon`, `.h-md`, `.body` |
| S19 | Dot-matrix Decoration | `dots`, `dots-fine`, `dot-mat` overlays | `dots`, `dots-fine`, `dot-mat`, `dot-mat.lg/xl/dense` |
| S20 | Number Mega | `num-mega` / `name-mega` large typographic | `num-mega`, `name-mega`, `name-mega.muted` |
| S21 | Bar Tower KPI | `bar-towers` + `bar-tower` | `bar-towers`, `bar-tower`, `.body-block`, `.b-accent`, `.lbl`, `.nb`, `.sub` |
| S22 | Photo / Image | Image slot with `data-image-slot` | `frame-img`, `data-image-slot` |
| SWISS-COVER-ASCII | ASCII Cover | ASCII matrix canvas | `canvas-card`, `ascii-bg`, `h-hero-zh` |
| SWISS-CLOSING-ASCII | ASCII Closing | ASCII matrix canvas | `canvas-card`, `ascii-bg` |

---

## Registered CSS Component Classes

### Layout / Grid
- `grid-12` — 12-column CSS grid

### Canvas Mode
- `canvas-card` — full-bleed card container
- `chrome-min` — compact chrome/foot (minimised)
- `ascii-bg` — ASCII matrix canvas background

### Headings
- `h-hero`, `h-hero-zh` — hero title (11vw / 8.4vw)
- `h-xl`, `h-xl-zh` — extra-large (6vw / 5vw)
- `h-statement` — statement heading `min(7.8vw, 13.4vh)` — **use for S03/S09/S10 only**
- `h-md` — medium heading
- `h-sub` — sub heading

### Cards
- `card-fill` — default grey card
- `card-ink` — dark inverted card
- `card-accent` — accent colored card
- `card-outlined` — outlined card
- `card-ink-outlined` — dark outlined card

### Sub-Grid Cards (S06 / S15)
- `sub-grid-3-2` — 3-column × 2-row grid
- `sub-card` — card in sub-grid (`.accent` / `.ink` variants)
- `nb-corner` — number badge in top-right corner
- `ttl` — card title
- `desc` — card description
- `lucide` — Lucide icon within card

### Stack Blocks (S14)
- `stack-row` — 3-column equal-height row
- `stack-block` — individual block
- `b-accent` / `b-grey` / `b-ink` — background variants
- `.layer-nb` — layer number
- `.layer-icon` — icon container
- `.layer-ttl` — layer title
- `.layer-desc` — layer description
- `.layer-tag` — top-border tag

### Split Layout
- `split-half` — 2-column split
- `.half` — individual half
- `b-grey` / `b-accent` / `b-ink` — background variants

### Numbers / KPI
- `kpi-hero`, `kpi-big`, `kpi-mid` — KPI numbers
- `kpi-thin`, `kpi-thin-sm` — thin-weight KPI
- `num-mega`, `name-mega` — mega typography
- `kpi-row-4` — 4-column KPI row
- `kpi-cell` — individual KPI cell

### Timeline
- `timeline-v`, `timeline-h` — vertical / horizontal
- `tl-node`, `th-node` — timeline node
- `.yr`, `.multi`, `.desc` — year / large number / description

### Charts
- `h-bar-chart` — horizontal bar chart
- `v-bar-chart` — vertical bar chart
- `.row-fill`, `.col-bar` — fill / bar elements

### Type Tokens
- `t-cat` — category / eyebrow label
- `t-meta` — meta / running header
- `t-helper` — helper / caption
- `t-body-sm`, `t-body`, `t-body-emp` — body text
- `t-h-prod` — productive heading

### Tags / Labels
- `kicker` — section kicker
- `tag` — inline tag (`.solid`, `.accent` variants)
- `meta` — mono meta
- `meta-row` — meta row with dot separators

### Decorations
- `rule`, `rule.thick`, `rule.accent` — rule lines
- `dots`, `dots-fine`, `dots-bold` — dot matrices
- `dot-mat`, `dot-mat.lg/xl/dense` — dot matrix patterns
- `ring-mat`, `ring-mat.lg` — ring matrix
- `cross-mat`, `cross-mat.lg` — cross/X matrix
- `hatch` — hatch pattern
- `geo-icon` — geometric icon container

### Motion
- `[data-anim]` — animation target
- `[data-anim="left/right/line"]` — directional animation

---

## Unregistered Classes (Do Not Use)

The following classes are **NOT** registered in this system. Decks using these will fail class whitelist validation:

- `sub-grid-3-2` — ✅ NOW REGISTERED (v1.0.0)
- `sub-card` — ✅ NOW REGISTERED (v1.0.0)
- `nb-corner` — ✅ NOW REGISTERED (v1.0.0)
- `stack-row` — ✅ NOW REGISTERED (v1.0.0)
- `stack-block` — ✅ NOW REGISTERED (v1.0.0)
- `b-grey` / `b-accent` / `b-ink` — ✅ NOW REGISTERED (v1.0.0)

All previously unregistered classes are now added to the canonical `template-swiss.html` as of v1.0.0.

---

## Chinese Title Font-Size Discipline

For Chinese hero titles, use double-constraint `min(Xvw, Yvh)` with **Y ≥ X × 1.6** to ensure non-overflow:

| Char count | Constraint |
|-----------|-----------|
| ≤ 8 chars, single line | `min(6.4vw, 11.2vh)` |
| ≤ 8 chars, 2-line | `min(5.8vw, 10.2vh)` |
| 9–12 chars, 2-line | `min(5.2vw, 9.2vh)` |

**Important**: In Canvas/Swiss mode, the hero title constraint should be `min(9.4vw, 15vh)` for long-form titles (12+ chars). The Y value (15vh) satisfies Y ≥ 9.4×1.6 = 15.04vh ≈ 15vh.

---

## Forbidden Patterns

1. **No P23/P24 experimental structures** — `swiss-img-split`, `Swiss Image Split`
2. **No `text-align:center` in non-statement headings** — titles must be left-aligned (exception: `h-statement` in S03/S09/S10)
3. **No `align-self:center` on `<h1>` or `<h2>` in heading areas** — use left-aligned or `h-statement` class
4. **No SVG `<text>` elements** — use HTML text only
5. **All images must have `data-image-slot` attribute**
6. **S22 images**: `object-position: center 35%` for portraits, `top center` for landscapes
