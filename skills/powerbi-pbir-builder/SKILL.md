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

Write report pages and visuals directly into an existing PBIP project's `.Report\definition`
folder, instead of clicking through Power BI Desktop by hand. Useful for generating many
similar visuals (a row of KPI cards, a page per region), or for scripting a layout once you
know the pattern.

Read this before any other reference in this skill: PBIR is a strict, brittle JSON format.
A single wrong bracket or an unknown property can stop the whole report from opening. Treat
every edit here as something to do carefully, not casually.

## When to use

Use this to ADD pages or visuals to a PBIP project that already exists. For choosing which
chart fits a question, picking colors, and general layout rules, use `powerbi-report-design`
first and bring the decision here to implement. For the model behind the visuals, use
`powerbi-modeling` and `powerbi-dax`. For safely hand editing the semantic model's TMDL, and
the general pbip safety rules, use `powerbi-project-and-tools`.

## Critical constraints, read first

1. **Never create a PBIP from scratch.** Power BI Desktop generates boilerplate (`report.json`,
   `.platform`, `version.json`, real GUIDs, theme registration) that is version specific and
   not practical to hand write. Always start from a PBIP the user already saved from Desktop.
2. **Power BI Desktop must be closed** while you write files. Desktop holds the project open
   and will overwrite your changes from its in memory copy on save, or the files may be locked.
3. **Back up first.** Copy the `.Report` folder, or make sure it is committed to git, before
   writing anything.
4. **Validate after writing.** Parse every JSON file you wrote before telling the user to
   reopen Desktop. A missing comma or bracket blocks the whole report from loading.
5. **Prefer the theme over bespoke visual formatting.** Put color and font choices in the
   report's theme JSON (see `house-default-theme.json` in the `powerbi-report-design` skill) rather than repeating them
   in every `visual.json`. Change it once, it applies everywhere.

## Workflow

1. Confirm a PBIP already exists and Power BI Desktop is closed. If there is no PBIP yet,
   stop and have the user create one: open Desktop, connect the data source, File, Save As,
   Power BI Project (.pbip).
2. Read `references/pbir-structure-and-safety.md` for the folder layout and the safe editing
   steps.
3. Detect the schemas already in use. The three file kinds use three different schemas, so
   take each from an existing file of the same kind, and for `visual.json` use the highest
   version in the project rather than the first one you open. Do not hardcode a version,
   Desktop's version changes over time. See `references/layout-and-schema-versions.md`.
4. Pick the visual type and query roles for what the user wants. Read
   `references/visual-types-and-patterns.md` for the catalog and worked examples. For a table,
   matrix, card, KPI, gauge, or textbox, start from the complete file in
   `references/templates-grids.md` or `references/templates-single-value.md`.
5. Work out layout using `references/layout-and-schema-versions.md`, which follows the same
   8 pixel grid as the `powerbi-report-design` skill. Check that `report.json` has
   `"useStylableVisualContainerHeader": true` before writing any container styling, because
   without it subtitles, dividers, shadows, and header tooltips silently do nothing.
6. Write the files: the page folder, `page.json`, each visual's folder and `visual.json`,
   then update `pages/pages.json` to add the new page to `pageOrder`.
7. Validate every JSON file you wrote parses cleanly.
8. Tell the user the files are written, Desktop must stay closed until now, and to reopen
   the `.pbip` to see the result.

## Rules of thumb

- Name pages and visuals descriptively (`pgOverview`, `vSalesBarChart`), not with random IDs.
  The `name` field inside a JSON file must match its folder name exactly.
- `Entity` and `Property` values in a field reference are the exact table and column or
  measure name from the semantic model, case sensitive. Check the TMDL if unsure.
- A slicer, chart axis, or table needs at least one query role filled (for example `Category`
  and `Y` for a bar chart, `Values` for a slicer). See the catalog for the exact roles.
- Keep conditional formatting logic in a model or extension measure that returns a color
  string, referencing the theme's semantic `good` and `bad` colors, rather than a hardcoded
  hex value repeated in many visuals.
- If the user wants a variance or actual versus plan style chart, that is a legitimate pattern
  (IBCS calls it a comparison chart), but use the house theme's colors for it, not a borrowed
  palette. See `powerbi-report-design` for the color rules.
- A title or a card can be bound to a measure that returns a string, so it updates with the
  filters. Watch the grain, the measure is read at the whole visual level, so a per row ratio
  measure overstates unless you aggregate it (a weighted total, or `AVERAGEX` over the entity). See
  `references/visual-types-and-patterns.md`.

## References in this skill

- `references/pbir-structure-and-safety.md`: the PBIR folder layout, the files you write
  versus the files only Desktop can generate, and the full safe editing checklist.
- `references/visual-types-and-patterns.md`: the visual type catalog and query roles, field
  reference shapes, letting a field parameter drive a role, and worked JSON for a trend chart,
  a slicer, and an image.
- `references/formatting-and-selectors.md`: where formatting lives, the selector forms and
  why the wrong one silently does nothing, referencing a theme color with `ThemeDataColor`, the
  container card that makes a report look finished, gradients, and reference lines.
- `references/cards-and-dynamic-text.md`: the new card's shape, the legacy card's
  remaining job, titles bound to a measure, and the grain trap that overstates them.
- `references/filters-and-sync.md`: the `filterConfig` shapes including excluding blanks
  properly, and slicer sync group naming.
- `references/templates-grids.md`: complete copyable `visual.json` files for a table and a
  matrix, with the column, header, and subtotal formatting each one needs.
- `references/templates-single-value.md`: complete copyable files for the legacy card, KPI,
  gauge, and textbox, including the textbox's own formatting grammar.
- `references/layout-and-schema-versions.md`: canvas, the grid densities with real numbers,
  the z and tab order bands Desktop writes, hiding a visual, and reading the schema
  version already in use instead of hardcoding one.
