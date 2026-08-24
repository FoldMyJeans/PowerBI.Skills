---
name: powerbi-report-design
description: >-
  Design the report layer of a Power BI file so it reads fast and looks professional: page and
  dashboard layout, choosing the right chart for the question, table and matrix design,
  conditional formatting, tooltips, native analytical visuals, color and theme JSON, fonts,
  slicers, bookmarks and navigation, the filter pane, and an accessibility pass. Use whenever
  the user is laying out a report or dashboard, asking which chart to use, picking colors or a
  color palette, writing or fixing a theme JSON, fixing bad fonts, adding slicers,
  bookmarks, drill through, or the filter pane, or wants to make a report
  look professional or clean up a busy page. Trigger on "design a report", "dashboard layout",
  "pick a chart", "choose colors", "theme JSON", "color palette", "slicers", "bookmarks",
  "filter pane", "accessibility", "matrix", "conditional formatting", "heatmap", "data bars",
  "tooltip", "decomposition tree", "key influencers", "small multiples". Assumes Power BI
  Pro only, no Fabric or Premium.
---

# Power BI report design

This skill covers the report layer: page layout, chart choice, color and theme, slicers and
navigation, and accessibility. The situational rules of thumb live in
`references/design-principles.md` and the ready made theme in
`references/house-default-theme.json`. This skill leans on both and adds the how-to. It
assumes Power BI Pro (no Fabric or Premium).

## When to use

Use this when laying out a report or dashboard, choosing a chart, picking colors or writing a
theme JSON, fixing fonts, adding slicers or bookmarks or navigation, setting up the filter
pane, or running an accessibility pass. For the model behind the report, the star schema, and
the `_Measures` table that feeds the visuals, use `powerbi-modeling`. For the measures
themselves use `powerbi-dax`. For the pbip and TMDL file format and external theme tooling use
`powerbi-project-and-tools`.

## The mental model

1. A report answers questions, it is not a wall of numbers. Decide the one question a page
   answers, then design the page to answer it in about 5 seconds.
2. Design once as a system. Put colors, fonts, and visual defaults in one theme JSON and reuse
   it everywhere. This is the single biggest lever for a consistent, professional look.
3. The chart follows the question, not taste. Comparison, trend, variance, correlation, and
   part to whole each have a right answer.

## Workflow

1. Start from the house theme. Apply `references/house-default-theme.json` in View, Themes,
   Browse for themes. It sets the Okabe-Ito colorblind safe palette, Segoe UI, and a blue to
   orange diverging scale that avoids red and green. Every visual then inherits safe defaults.
   See `references/color-and-theme.md`.
2. Choose the layout. Canvas 16:9 at 1280x720, everything on an 8 pixel grid, about six to eight
   visuals per page. Answer first at the top, the "why" charts below, detail last. See
   `references/layout-and-charts.md` for the grid numbers and
   `references/design-principles.md` for the house page conventions.
3. Pick charts by the question. Bar or column for comparison, line for trend, waterfall for
   variance, scatter for correlation and outliers, small multiples instead of many overlapping
   lines. Avoid pie, donut, and gauge unless it is a small part to whole. Always pair a number
   with a comparison (target, prior period, benchmark). Use a table for a flat list and a matrix
   for a hierarchy or cross tab, and reach for the Pro safe native analytical visuals
   (decomposition tree, key influencers) when the question is "why". See
   `references/layout-and-charts.md`, `references/tables-and-matrix.md`, and
   `references/analytical-visuals.md`.
4. Apply color and type. Three to five purposeful colors, each with a fixed meaning. Use the good
   and bad slots (green and orange) for good and bad and avoid a true red to green pairing, and
   never let a brand color override a semantic slot. Segoe UI for text, and keep the size scale
   tight. See `references/color-and-theme.md`.
5. Add slicers and navigation. Keep about 5 slicers visible, then switch to dropdowns. Sync
   slicers across pages and always offer a Clear all. Use buttons plus bookmarks for app like
   navigation and a back button for drill through. Name every object in the Selection and
   Bookmarks panes. See `references/slicers-and-navigation.md`.
6. Run the accessibility check. Contrast at least 4.5 to 1 for text and 3 to 1 for bars and
   icons, alt text on every non decorative visual, a logical tab order in the Selection pane,
   and never color as the only signal. See `references/accessibility.md`.
7. Add tooltips, and conditional formatting only if asked. Give every non-obvious chart or table
   a short plain-English tooltip that says what it shows, so a future reader gets it at a glance.
   Conditional formatting is opt-in: build the visual plain, then ask the user before adding any
   color, heatmap, data bars, or icons. See `references/conditional-formatting.md`.
8. Write insight driven titles. Title a visual with the takeaway, not the field name. "Revenue
   is 12 percent below target" beats "Revenue by Month". For a title that stays true as filters
   change, bind it to a measure that returns a string. See the `powerbi-pbir-builder` skill for the
   shape and the grain caveat (a per row ratio measure overstates at the whole visual level).

## Rules of thumb

- 5 second rule and one decision per page. If the main point takes longer than 5 seconds
  to read, the page is doing too much. Cut anything that does not serve the question.
- Density limit. About 6 to 8 visuals and 10 to 20 fields per page. This helps
  readability and render performance.
- Reading path. Most eyes go top left first, then across and down. Put the most important
  visual top left.
- Declutter. Drop heavy borders, background fills, redundant gridlines, and legends you do not
  need. Less non data ink means less to process.
- Three to five colors with fixed meaning. Gray for context, one accent for the thing in focus,
  and the semantic pair (green and a red orange, never a true red against green) for good
  versus bad.
- Name every object. In the Selection and Bookmarks panes, so future you can maintain it.
- Native visuals first. Stock visuals plus DAX cover most reports. Treat a third-party visual as
  a deliberate, governed exception, exactly one, with its source and license noted.
- The full list of rules and when to bend them is in `references/design-principles.md`. A dense
  export page for one analyst is allowed to break the 5 second rule.

## Pro vs Premium

Report design, themes, slicers, bookmarks, the filter pane, tables, matrices, and conditional
formatting are all Pro safe. The native analytical and AI visuals are Pro safe too, because their
AI runs in the Power BI engine, not in Copilot: the decomposition tree (including its High and
Low value AI), key influencers, native small multiples, the new card visual, and the KPI visual.
See `references/analytical-visuals.md`. Flag these as needing Fabric or Premium, not Pro: Copilot
and any Copilot authored narrative, applying a theme to a published dataset over the XMLA
endpoint, and programmatic theme extraction through Semantic Link Labs (it runs in a Fabric
notebook). Smart narrative in Custom mode and the free theme generators (themes.powerbi.tips,
bibb.pro) are Pro safe. The Q&A visual is Pro safe but is on a retirement path
(around December 2026), so do not build new reports around it.

## References in this skill

- `references/layout-and-charts.md`: canvas and the 8 pixel grid, the three tier layout, the
  5 second rule and density limits, and choosing a chart by the question.
- `references/color-and-theme.md`: the theme JSON structure slot by slot, how to apply and
  validate the house theme, color rules, and fonts.
- `references/slicers-and-navigation.md`: slicer types, syncing and Clear all, buttons and
  bookmarks, drill through, and filter pane formatting.
- `references/accessibility.md`: WCAG contrast, alt text, tab order, color as the only signal,
  and the free tools to check a live canvas.
- `references/tables-and-matrix.md`: table vs matrix, layouts and subtotals, native sparklines,
  column width, and the scrollable table performance trap.
- `references/conditional-formatting.md`: the opt-in rule, the three modes, the field value color
  pattern, data bars and icons, and why the theme cannot store the rules.
- `references/analytical-visuals.md`: the Pro safe native analytical and AI visuals, the
  decomposition tree, key influencers, small multiples, and the new card and KPI visuals.
