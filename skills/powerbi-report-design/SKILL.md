---
name: powerbi-report-design
description: >-
  Design the report layer of a Power BI file, plain, executive or creative, so it reads fast:
  page and dashboard layout, choosing the right chart for the question, table and
  matrix design, conditional formatting, tooltips, native analytical visuals, color and theme
  JSON, fonts, slicers, bookmarks and navigation, the filter pane, and an accessibility pass. Use
  whenever the user is laying out a report or dashboard, asking which chart to use, picking colors
  or a color palette, writing or fixing a theme JSON, fixing bad fonts, adding slicers, bookmarks,
  drill through, or the filter pane, or wants to make a report look professional or clean up a busy
  page. Trigger on "design a report", "dashboard layout", "pick a chart", "choose colors", "theme
  JSON", "color palette", "slicers", "bookmarks", "filter pane", "accessibility", "matrix",
  "conditional formatting", "heatmap", "data bars", "tooltip", "decomposition tree", "key
  influencers", "small multiples". Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI report design

Checked against Power BI releases through October 2026.

The report layer: page layout, chart choice, color and theme, slicers and navigation,
accessibility. The judgement rules live in `references/design-principles.md`, the default theme in
`references/house-default-theme.json`. For the model and the `_Measures` table use
`powerbi-modeling`, for measures `powerbi-dax`, for pbip and TMDL files and theme tooling
`powerbi-project-and-tools`, for writing visuals into a PBIP `powerbi-pbir-builder`.

## First, which look

Every kind of report is in scope: a plain practical dashboard, a polished executive page, a
creative page with charts inside tables or custom visuals, a routine operational page.

- The report already has a look (its own theme, grid, card style): follow it. Never restyle a
  report toward the defaults here as a side effect of another change.
- It has no look of its own: start from the defaults in this skill (the theme, the 8 pixel grid,
  the default conventions in `design-principles.md`). They are a starting point that works, not a
  requirement.
- The judgement applies to every style: one question per page, no two visuals restating a fact,
  a comparison beside every number, accessibility.

## Workflow

1. Decide the one question the page answers, readable in about 5 seconds.
2. Theme. With no existing look, apply `references/house-default-theme.json` (View, Themes,
   Browse for themes): Okabe-Ito colorblind safe palette, Segoe UI, a blue to orange diverging
   scale with no red to green. Check the report's base theme first, Fluent 2 or Classic changes
   what every visual inherits. See `references/color-and-theme.md`.
3. Layout. Keep the report's page size (Fluent 2 starts at 1920x1080, older reports 1280x720),
   an 8 pixel grid, about six to eight visuals. Answer on top, the "why" charts below, detail
   last. See `references/layout-and-charts.md`.
4. Charts by the question. Bar or column to compare, line for trend, waterfall for variance,
   scatter for correlation, small multiples over many overlapping lines. Pie, donut and gauge only
   for a small part to whole. Table for a flat list, matrix for a hierarchy or cross tab,
   decomposition tree or key influencers for "why". See `references/layout-and-charts.md`,
   `references/tables-and-matrix.md`, `references/analytical-visuals.md`.
5. Color and type. Three to five colors with fixed meaning, good and bad slots for good and bad,
   no true red against green, no brand color over a semantic slot. See
   `references/color-and-theme.md`.
6. Slicers and navigation. About 5 visible slicers, then dropdowns or the filter pane. Sync
   across pages, always a Clear all, buttons plus bookmarks or field parameters for views, a back
   button for drill through. Name every object. See `references/slicers-and-navigation.md`.
7. Accessibility. Contrast 4.5 to 1 for text, 3 to 1 for bars and icons, alt text on every non
   decorative visual, a set tab order, never color as the only signal. See
   `references/accessibility.md`.
8. Tooltips, and conditional formatting only if asked. Give every non-obvious chart or table a
   short plain-English tooltip. Build visuals plain, then ask before adding color, heatmaps, data
   bars or icons. See `references/conditional-formatting.md`.
9. Titles. The default is a neutral title that names the chart, with no analysis in it. A
   storytelling or executive page may use a takeaway title ("Revenue is 12 percent below target"),
   bound to a measure that returns a string so it stays true as filters change. See the
   `powerbi-pbir-builder` skill for the binding and the grain trap (a per row ratio measure
   overstates at the whole visual level).

## Rules of thumb

- One decision per page. Cut anything that does not serve the question. A crowded page works the
  declutter ladder in `design-principles.md` before it splits.
- Density. About 6 to 8 visuals and 10 to 20 fields per page, for reading and render speed.
- Reading path. The most important visual top left.
- Declutter. Drop heavy borders, fills, redundant gridlines and legends you do not need.
- Name every object in the Selection and Bookmarks panes.
- Native visuals first. Third-party visuals are fine when they work in the Service and look good,
  one or two per report unless the owner asks for more, with source and license noted. To build
  one, use `powerbi-custom-visuals`.
- When to bend all of this (an export page, an alert wall, a one number scorecard) is in
  `design-principles.md`.

## Pro vs Premium

Pro safe: report design, themes, slicers, bookmarks, the filter pane, tables, matrices,
conditional formatting, and the native analytical visuals (decomposition tree with its High and
Low value AI, key influencers, small multiples, the new card, the KPI visual), because their AI
runs in the engine, not Copilot. Smart narrative in Custom mode and the free theme generators
(themes.powerbi.tips, bibb.pro) are Pro safe. Needs Fabric or Premium: Copilot and any Copilot
authored narrative, applying a theme to a published dataset over XMLA, and theme extraction
through Semantic Link Labs (a Fabric notebook). The Q&A visual is Pro safe but retiring around
December 2026, so do not build new reports around it. See `references/analytical-visuals.md`.

## Beyond native charts

`powerbi-chart-recipes` builds charts Power BI lacks (beeswarm, waffle, filter drawer, charts
inside table cells) with a screenshot of each to show the owner. `references/visual-decisions.md`
records which ones the owner wants where.

## References in this skill

- `references/design-principles.md`: the judgement rules, the default conventions, custom visuals,
  asset discipline, the declutter ladder, and when to bend the rules.
- `references/layout-and-charts.md`: canvas and grid, the three tier layout, choosing a chart by
  the question.
- `references/color-and-theme.md`: theme JSON slot by slot, the base theme, applying and
  validating the default theme, color rules, fonts.
- `references/house-default-theme.json`: the default theme for a report with no look of its own.
- `references/slicers-and-navigation.md`: slicer types, sync and Clear all, buttons and
  bookmarks, field parameters, drill through, the filter pane.
- `references/tables-and-matrix.md`: table vs matrix, layouts and subtotals, column width,
  sparklines, the scrollable table trap.
- `references/conditional-formatting.md`: the opt-in rule, the pattern menu, the three modes,
  measure driven color, data bars and icons.
- `references/accessibility.md`: contrast, alt text, tab order, color as the only signal, the
  checks to run on a PBIP.
- `references/analytical-visuals.md`: the Pro safe native analytical and AI visuals.
- `references/visual-decisions.md`: what the owner liked and rejected when shown real examples,
  and why. Check it before proposing a visual, add to it after each decision.
