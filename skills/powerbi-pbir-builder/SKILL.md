---
name: powerbi-pbir-builder
description: >-
  Write real report pages and visuals directly into an existing PBIP project by authoring
  PBIR JSON (page.json and visual.json) files. Use whenever the user wants to generate a
  report page, add a visual programmatically, build a KPI card, create a bar or line or area
  chart in code, add a slicer through code, automate a report layout, or clone a visual
  pattern across many pages, instead of clicking through Power BI Desktop by hand. Trigger on
  phrases like "add a page to the report", "write PBIR JSON", "generate this chart in code",
  "build a KPI card", "add a slicer", "automate the report layout", "create these visuals
  programmatically". Only adds to a PBIP that already exists. Does not create a PBIP from
  scratch, and does not replace Power BI Desktop for report design decisions, use
  `powerbi-report-design` for that. Assumes Power BI Pro only, no Fabric or Premium.
---

# Power BI PBIR builder

Checked against Power BI releases through October 2026.

Write pages and visuals straight into an existing PBIP's `.Report\definition` folder. Worth it
for many similar visuals (a row of KPI cards, a page per region) or a layout you script once.
PBIR is strict JSON: one wrong bracket or one unknown property can stop the whole report from
opening.

## When to use

Only to ADD pages or visuals to a PBIP that exists. Chart choice, colour and layout rules come
from `powerbi-report-design`, then get implemented here. The model behind the visuals is
`powerbi-modeling` and `powerbi-dax`. TMDL hand editing and general pbip safety are
`powerbi-project-and-tools`.

## Critical constraints

1. **Never create a PBIP from scratch.** Desktop writes `report.json`, `.platform`,
   `version.json`, real GUIDs and the theme registration, all version specific. Start from a PBIP
   the user saved from Desktop.
2. **Desktop must be closed** while you write. It overwrites your changes from its in memory copy
   on save, or locks the files. The Desktop Bridge branch is in `agent-verification.md` in the
   `powerbi-project-and-tools` skill.
3. **Back up first.** Copy the `.Report` folder or commit it to git.
4. **Parse every JSON file you wrote** before the user reopens Desktop. A missing comma blocks the
   whole report. Parsing is the first check, not the last (workflow step 7).
5. **Theme before per visual formatting.** Colour and font go in the report's theme JSON once, not
   in every `visual.json`. When the report has no theme of its own, start from
   `house-default-theme.json` in the `powerbi-report-design` skill. Classic slicer `dropdown`
   properties in a theme were ignored in one report, so render one page after a theme change (see
   `references/slicer-templates.md`).

## Workflow

1. Confirm a PBIP exists and Desktop is closed. No PBIP: the user opens Desktop, connects the
   source, then File, Save As, Power BI Project (.pbip).
2. Read `references/pbir-structure-and-safety.md` for the folder layout and the safety checklist.
3. Detect the schemas in use. Three file kinds, three schemas. Take each from a file of the same
   kind, and for `visual.json` use the highest version in the project. Never hardcode one. See
   `references/layout-and-schema-versions.md`.
4. Pick the visual type and query roles from `references/visual-types-and-patterns.md`. For a
   table, matrix, card, KPI, gauge or textbox, start from the complete file in
   `references/templates-grids.md` or `references/templates-single-value.md`.
5. Lay out with `references/layout-and-schema-versions.md` (the same 8 pixel grid as
   `powerbi-report-design`). Before any container styling, check that `report.json` has
   `"useStylableVisualContainerHeader": true` (a new Fluent 2 report may already have it). Without
   it, subtitles, dividers, shadows and header tooltips silently do nothing.
6. Write the page folder, `page.json`, each visual folder and `visual.json`, then add the page to
   `pageOrder` in `pages/pages.json`.
7. Parse every file, then run the completion loop in `agent-verification.md` in the
   `powerbi-project-and-tools` skill: conformance validation, reload and screenshot through the
   Desktop Bridge, the review checklist, and the expected numbers asserted with DAX. Valid JSON can
   render wrong, and a page that renders can show a wrong total.
8. Report what the loop showed and name any step that was blocked. Without the bridge, tell the
   user the files are written, to reopen the `.pbip` now, and to run the same review and number
   checks.

## Rules of thumb

- Descriptive names (`pgOverview`, `vSalesBarChart`), not random IDs. The `name` inside a file
  must equal its folder name exactly.
- `Entity` and `Property` in a field reference are the exact model names, case sensitive. Check
  the TMDL.
- A slicer, chart axis or table needs at least one query role filled (`Category` and `Y` for a
  bar chart, `Values` for a slicer). Exact roles are in the catalog.
- Conditional formatting: a model or extension measure that returns a colour string, built on the
  theme's semantic `good` and `bad` colours, not a hex repeated across visuals.
- A variance or actual versus plan chart (IBCS calls it a comparison chart) is fine. Colour it from
  the report's theme, not a borrowed palette. Colour rules are in `powerbi-report-design`.
- A title or card bound to a string measure updates with the filters. It is read at the whole
  visual grain, so a per row ratio overstates unless aggregated (a weighted total, or `AVERAGEX`
  over the entity). See `references/cards-and-dynamic-text.md`.

## References in this skill

- `references/pbir-structure-and-safety.md`: folder layout, the files you write versus the files
  only Desktop generates, `pages.json`, the safety checklist, and respecting a hand tuned layout.
- `references/visual-types-and-patterns.md`: visual type catalog and query roles (with what was
  seen in a saved file and what is a guess), field references, field parameters, and worked JSON
  for a trend chart and a slicer.
- `references/formatting-and-selectors.md`: where formatting lives, the selector forms and why
  the wrong one silently does nothing, `ThemeDataColor`, the container card block, and gradients.
- `references/formatting-charts-and-tables.md`: line series colour, data labels on bars,
  reference lines, table and matrix column widths (the 2026 width model), and chart properties
  added in 2026.
- `references/cards-and-dynamic-text.md`: the new card's shape, the legacy card's remaining job,
  titles bound to a measure, and the grain trap that overstates them.
- `references/filters-and-sync.md`: `filterConfig` shapes including excluding blanks properly,
  and slicer sync group naming.
- `references/slicer-templates.md`: the classic underline dropdown, the date picker and slider,
  the button slicer with its state selectors, and the traps each one hit.
- `references/list-slicer-dropdown.md`: the list slicer in dropdown mode, a wide open list from a
  narrow box. Template, the Fit to space row trap, sizing from the data, and converting a classic
  slicer.
- `references/templates-grids.md`: complete `visual.json` files for a table and a matrix.
- `references/templates-single-value.md`: complete files for the legacy card, KPI, gauge and
  textbox, plus the image visual, a page background picture, and an image bound to an SVG measure.
- `references/layout-and-schema-versions.md`: canvas and `page.json`, grid densities with real
  numbers, the z and tab order bands Desktop writes, hiding a visual, and detecting the schema
  version instead of hardcoding one.
